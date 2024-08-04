""" APT helper functions """
import glob
import gzip
import logging
import lzma
import os
import tempfile
import time
import json

from typing import Optional, Any, Tuple
from urllib.parse import urlparse

import requests

from .deb import Package
from .fake import Fake
from .version import parse_depends, VersionDepends, PackageRelation, Version


class Apt:
    """ Get packages from apt repositories. """

    id: str
    url: str
    distro: str
    components: list[str]
    arch: str
    packages: Optional[dict[str, list[Package]]] = {}
    index_loaded: bool
    state_folder: str
    key_url: Optional[str]
    key_gpg: Optional[str]
    has_sources: bool

    @classmethod
    def from_config(cls, repo_config: dict[str, Any], arch: str):
        """ Get an apt repositry for a config entry. """
        if 'apt_repo' not in repo_config:
            return None

        if 'distro' not in repo_config:
            return None

        return cls(
            url=repo_config['apt_repo'],
            distro=repo_config['distro'],
            components=repo_config.get('components', None),
            key_url=repo_config.get('key', None),
            key_gpg=repo_config.get('gpg', None),
            arch=arch
        )

    @classmethod
    def ebcl_apt(cls, arch: str, release: str = '1.2'):
        """ Get the EBcL apt repo. """
        return cls(
            url=f'http://linux.elektrobit.com/eb-corbos-linux/{release}',
            distro='ebcl',
            components=['prod', 'dev'],
            arch=arch,
            key_url='file:///build/keys/elektrobit.pub',
            key_gpg='/etc/berrymill/keyrings.d/elektrobit.gpg'
        )

    def __init__(
        self,
        url: str = "http://archive.ubuntu.com/ubuntu",
        distro: str = "jammy",
        components: Optional[list[str]] = None,
        key_url: Optional[str] = None,
        key_gpg: Optional[str] = None,
        has_sources: bool = True,
        arch: str = "amd64",
        state_folder: str = '/workspace/state/apt'
    ) -> None:
        if components is None:
            components = ['main']

        self.url = url
        self.distro = distro
        self.components = components
        self.arch = arch
        self.packages = None
        self.state_folder = state_folder
        self.key_url = key_url
        self.key_gpg = key_gpg
        self.has_sources = has_sources

        if not key_gpg and 'ubuntu.com/ubuntu' in url:
            self.key_gpg = '/etc/apt/trusted.gpg.d/ubuntu-keyring-2018-archive.gpg'
            logging.info('Using default Ubuntu key %s for %s.',
                         self.key_gpg, self.url)

        if os.path.isfile(self.state_folder):
            self.state_folder = os.path.dirname(self.state_folder)

        if not os.path.exists(self.state_folder):
            os.makedirs(self.state_folder, exist_ok=True)

        # Generate repo id
        try:
            uo = urlparse(self.url)
        except Exception as e:
            logging.error(
                'Invalid apt url %s, cannot geneate id! %s', self.url, e)
            return None

        cmp_str = '_'.join(self.components)

        self.id = f'{uo.netloc}_{self.distro}_{cmp_str}'

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Apt):
            return False

        if len(self.components) != len(value.components):
            return False

        for component in self.components:
            if component not in value.components:
                return False

        return value.distro == self.distro and \
            value.url == self.url and \
            value.arch == self.arch

    def _load_index(self):
        """ Download repo metadata and parse package indices. """
        package_indexes = self._download_distro()
        if not package_indexes:
            return

        if self.packages is None:
            self.packages = {}

        for component in self.components:
            pkg_cnt = len(self.packages)

            if component in package_indexes:
                url: str = package_indexes[component]
                self._parse_component(url)
            else:
                logging.warning(
                    'No package index for component %s found!', component)

            new_pkgs = len(self.packages) - pkg_cnt
            logging.info('Found %s packages in component %s of %s',
                         new_pkgs, component, self)

        logging.info('Repo %s provides %s packages.',
                     self, len(self.packages))

    def _parse_component(self, url: str):
        """ Parse component package index. """
        assert self.packages is not None

        packages = f'{self.url}/dists/{self.distro}/{url}'

        data = self._download_url(packages)
        if not data:
            logging.error('Download of component %s failed!', url)
            return

        if url.endswith('xz'):
            content_bytes = lzma.decompress(data)
        else:
            assert url.endswith('gz')
            content_bytes = gzip.decompress(data)
        content: str = content_bytes.decode(
            encoding='utf-8', errors='ignore')
        lines: list[str] = content.split('\n')

        package = None
        for line in lines:
            line = line.strip()

            if not line:
                # package separator
                package = None
                continue

            if line.startswith('Package:'):
                # new package
                parts = line.split(' ')
                package = Package(parts[-1], self.arch, self.id)

            elif line.startswith('Filename:'):
                assert package is not None
                parts = line.split(' ')
                package.file_url = f'{self.url}/{parts[-1]}'

                if package.name not in self.packages:
                    self.packages[package.name] = [package]
                else:
                    self.packages[package.name].append(package)

            elif line.startswith('Depends:'):
                assert package is not None
                deps = line[8:].strip()
                package.depends = self._process_relation(
                    package.name, deps, PackageRelation.DEPENDS)

            elif line.startswith('Pre-Depends:'):
                assert package is not None
                deps = line[12:].strip()
                package.pre_depends = self._process_relation(
                    package.name, deps, PackageRelation.PRE_DEPENS)

            elif line.startswith('Recommends:'):
                assert package is not None
                deps = line[11:].strip()
                package.recommends = self._process_relation(
                    package.name, deps, PackageRelation.RECOMMENDS)

            elif line.startswith('Suggests:'):
                assert package is not None
                deps = line[9:].strip()
                package.suggests = self._process_relation(
                    package.name, deps, PackageRelation.SUGGESTS)

            elif line.startswith('Enhances:'):
                assert package is not None
                deps = line[9:].strip()
                package.enhances = self._process_relation(
                    package.name, deps, PackageRelation.ENHANCES)

            elif line.startswith('Breaks:'):
                assert package is not None
                deps = line[7:].strip()
                package.breaks = self._process_relation(
                    package.name, deps, PackageRelation.BREAKS)

            elif line.startswith('Conflicts:'):
                assert package is not None
                deps = line[10:].strip()
                package.conflicts = self._process_relation(
                    package.name, deps, PackageRelation.CONFLICTS)

            elif line.startswith('Version:'):
                assert package is not None
                package.version = Version(line[8:].strip())

    def _download_distro(self) -> Optional[dict[str, str]]:
        """ Download and parse distro release file. """
        inrelease = f'{self.url}/dists/{self.distro}/InRelease'

        data = self._download_url(inrelease)
        if not data:
            return None

        content = data.decode(encoding='utf-8', errors='ignore')

        package_indexes: dict[str, str] = {}

        for line in content.split('\n'):
            for component in self.components:
                search = f'{component}/binary-{self.arch}/Packages.xz'
                search2 = f'{component}/binary-{self.arch}/Packages.gz'
                if search in line or search2 in line:
                    line = line.strip()
                    parts = line.split(' ')
                    package_indexes[component] = parts[-1]

        logging.debug('Package indexes: %s', package_indexes)

        return package_indexes

    def _process_relation(
        self, name: str, relation: str, package_relation: PackageRelation
    ) -> list[list[VersionDepends]]:
        """ Parse relation string from stanza. """
        deps: list[list[VersionDepends]] = []

        for rel in relation.split(','):
            dep = parse_depends(rel.strip(), self.arch, package_relation)
            if dep:
                deps.append(dep)
            else:
                logging.error('Invalid package relation %s to %s for %s.',
                              rel.strip(), package_relation, name)

        return deps

    def find_package(self, package_name: str) -> Optional[list[Package]]:
        """ Find a binary deb package. """
        if self.packages is None:
            self._load_index()

        assert self.packages is not None

        if package_name in self.packages:
            return self.packages[package_name]
        else:
            return None

    def __str__(self) -> str:
        return f'Apt<{self.url}, {self.distro}, {self.components}, ' \
            f'key: {self.key_url}, gpg: {self.key_gpg}>'

    def __repr__(self) -> str:
        return self.__str__()

    def _download_url(self, url: str) -> Optional[bytes | Any]:
        """ Download the given url. """
        # Check for cached data.
        cache_file_name = url[7:].replace('/', '_')
        cache_file_path = os.path.join(self.state_folder, cache_file_name)

        cache_files = glob.glob(f'{cache_file_path}_*')
        if cache_files:
            cache_files.sort()
            cache_file = cache_files[-1]

            logging.debug('Cache file found for %s: %s', url, cache_file)

            ts_str = cache_file.split('_')[-1]
            ts = float(ts_str)
            age = time.time() - ts

            if age > 24 * 60 * 60:
                # older than one day
                logging.debug('Removing outdated cache file %s', cache_file)
                try:
                    os.remove(cache_file)
                except Exception as e:
                    logging.error(
                        'Removing old cache file %s failed! %s', cache_file, e)
            else:
                # Read cached data
                with open(cache_file, 'rb') as f:
                    logging.debug('Reading cached data from %s...', cache_file)
                    try:
                        return f.read()
                    except Exception as e:
                        logging.error(
                            'Reading cached data from %s failed! %s', cache_file, e)
        else:
            logging.info('No cache file found for %s', url)

        # Download the url
        try:
            result = requests.get(url, allow_redirects=True, timeout=10)
        except Exception as e:
            logging.error('Downloading %s failed! %s', url, e)
            return None

        if result.status_code != 200:
            return None

        # Cache the file
        save_file = f'{cache_file_path}_{time.time()}'

        file_bytes: bytes = b''
        with open(save_file, 'wb') as f:
            for chunk in result.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    file_bytes += chunk
                    f.write(chunk)

        return file_bytes

    def _cache_url(self, url: str, data: Any):
        """ Cache the data of an url. """
        cache_file_name = url[7:].replace('/', '_')
        cache_file_path = os.path.join(self.state_folder, cache_file_name)

        save_file = f'{cache_file_path}_{time.time()}'
        with open(save_file, 'w', encoding='utf8') as f:
            logging.info('Caching package indices as %s', save_file)
            try:
                json.dump(data, f)
            except Exception as e:
                logging.error(
                    'Caching package indices as %s failed! %s', save_file, e)

    def _get_data_for_url(self, url: str) -> Optional[Any]:
        """ Get cache data for url. """
        # TODO: test for fast on second try
        cache_file_name = url[7:].replace('/', '_')
        cache_file_path = os.path.join(self.state_folder, cache_file_name)

        cache_files = glob.glob(f'{cache_file_path}_*')
        if cache_files:
            cache_files.sort()
            cache_file = cache_files[-1]
            logging.info('Cache file found for %s: %s', url, cache_file)
            ts_str = cache_file.split('_')[-1]
            ts = float(ts_str)
            age = time.time() - ts
            if age > 24 * 60 * 60:
                # older than one day
                logging.debug('Removing outdated cache file %s', cache_file)
                try:
                    os.remove(cache_file)
                except Exception as e:
                    logging.error(
                        'Removing old cache file %s failed! %s', cache_file, e)
            else:
                # Read cached data
                with open(cache_file, encoding='utf8') as f:
                    logging.debug('Reading cached data from %s...', cache_file)
                    try:
                        data = json.load(f)
                        # Return cached data
                        return data
                    except Exception as e:
                        logging.error(
                            'Reading cached data from %s failed! %s', cache_file, e)
        else:
            logging.info('No cache file found for %s', url)

        return None

    def get_key(self) -> Optional[str]:
        """ Get key for this repo. """
        # TODO: test
        if not self.key_url:
            return None

        key_url = self.key_url
        if key_url.startswith('file://'):
            key_url = key_url[7:]

        contents = None

        if os.path.isfile(key_url):
            # handle local file
            logging.info('Reading key for %s from %s', self, key_url)
            with open(key_url, encoding='utf8') as f:
                contents = f.read()
        elif key_url.startswith('http://') or key_url.startswith('https://'):
            # download key
            logging.info('Downloading key for %s from %s', self, key_url)
            data = self._download_url(key_url)
            if data:
                contents = data.decode(encoding='utf8', errors='ignore')
            else:
                logging.error(
                    'Download of key %s for %s failed!', key_url, self)
        else:
            logging.error(
                'Unknown key url %s, cannot download key!', self.key_url)
            return None

        return contents

    def get_id(self) -> Optional[str]:
        """ Get identifier for this repo. """
        return self.id

    def get_key_files(
            self, output_folder: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """ Get gpg key file for repo key. """
        # TODO: test
        if not self.key_url:
            return (None, self.key_gpg)

        contents = self.get_key()
        if not contents:
            return (None, self.key_gpg)

        key_pub_file = None
        key_gpg_file = None
        if output_folder:
            key_pub_file = os.path.join(output_folder, f'{self.get_id()}.pub')
            key_gpg_file = os.path.join(output_folder, f'{self.get_id()}.gpg')
        else:
            key_pub_file = tempfile.mktemp()
            key_gpg_file = tempfile.mktemp()

        try:
            with open(key_pub_file, 'w', encoding='utf8') as f:
                f.write(contents)
        except Exception as e:
            logging.error('Writing pub key of %s to %s failed! %s',
                          self, key_pub_file, e)
            return (None, self.key_gpg)

        if not self.key_gpg:
            fake = Fake()
            try:
                fake.run_no_fake(
                    f'cat {key_pub_file} | gpg --dearmor > {key_gpg_file}')
            except Exception as e:
                logging.error('Dearmoring key %s of %s as %s failed! %s',
                              key_pub_file, self, key_gpg_file, e)
                return (key_pub_file, None)
        else:
            key_gpg_file = self.key_gpg

        return (key_pub_file, key_gpg_file)
