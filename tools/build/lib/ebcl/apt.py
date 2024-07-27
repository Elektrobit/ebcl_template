""" APT helper functions """
import gzip
import logging
import lzma
import os
import shutil

from typing import Dict, Optional

import requests

from ebcl.cache import Cache


class Package:
    """ APT package information. """
    name: str
    version: str
    arch: str
    file_url: str
    depends: list[str]
    stanza: dict[str, str]
    repo_url: str
    distro: str
    component: str

    def __init__(self, name: str):
        self.name = name
        self.depends = []
        self.stanza = {}

    def download(
        self, location: Optional[str] = None,
        cache: Optional[Cache] = None
    ) -> Optional[str]:
        """ Download this package. """
        if location is None:
            if cache is not None:
                # If no location is give, but cache, then download to cache.
                location = cache.folder
            else:
                location = '/tmp'

        # Test if package is in cache.
        if cache is not None:
            file = cache.get(self.arch, self.name, self.version)
            if file is not None and os.path.isfile(file):
                # Use package form cache.
                logging.info('Cache hit for package %s/%s/%s.',
                             self.name, self.version, self.arch)
                dst = os.path.join(location, os.path.basename(file))
                if file != dst:
                    shutil.copy(file, dst)
                return dst

        # Download package.
        result = requests.get(self.file_url, allow_redirects=True, timeout=10)
        if result.status_code != 200:
            return None
        else:
            local_filename = self.file_url.split('/')[-1]
            local_filename = os.path.join(location, local_filename)
            with open(local_filename, 'wb') as f:
                for chunk in result.iter_content(chunk_size=512 * 1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

        # Add package to cache.
        if cache is not None:
            cache.add(local_filename)

        return local_filename

    def get_depends(self) -> list[str]:
        """ Get dependencies. """
        return [dep.split(' ')[0].strip() for dep in self.depends]


class Apt:
    """ Get packages from apt repositories. """

    def __init__(
        self,
        url: str = "http://archive.ubuntu.com/ubuntu",
        distro: str = "jammy",
        components: Optional[list[str]] = None,
        arch: str = "amd64"
    ) -> None:
        if components is None:
            components = ['main']

        self.url = url
        self.distro = distro
        self.components = components
        self.arch = arch
        self.packages = {}  # type: Dict[str, Package]
        self._load_index()

    def _load_index(self):
        inrelease = f'{self.url}/dists/{self.distro}/InRelease'
        response = requests.get(inrelease, allow_redirects=True, timeout=10)
        content = response.content.decode(encoding='utf-8', errors='ignore')

        package_indexes: dict[str, str] = {}

        for line in content.split('\n'):
            for component in self.components:
                search = f'{component}/binary-{self.arch}/Packages.xz'
                search2 = f'{component}/binary-{self.arch}/Packages.gz'
                if search in line or search2 in line:
                    line = line.strip()
                    parts = line.split(' ')
                    package_indexes[component] = parts[-1]

        logging.info('Package indexes: %s', package_indexes)

        for component in self.components:
            if component in package_indexes:
                url: str = package_indexes[component]
                packages = f'{self.url}/dists/{self.distro}/{url}'
                response = requests.get(
                    packages, allow_redirects=True, timeout=10)

                if url.endswith('xz'):
                    content = lzma.decompress(response.content)
                else:
                    assert url.endswith('gz')
                    content = gzip.decompress(response.content)
                content = content.decode(encoding='utf-8', errors='ignore')
                content = content.split('\n')

                package = None
                for line in content:
                    line = line.strip()

                    if not line:
                        # package separator
                        package = None
                        continue

                    if line.startswith('Package:'):
                        # new package
                        parts = line.split(' ')
                        package = Package(parts[-1])
                        package.arch = self.arch
                        package.repo_url = self.url
                        package.distro = self.distro
                        package.component = component
                    elif line.startswith('Filename:'):
                        assert package is not None
                        parts = line.split(' ')
                        package.file_url = f'{self.url}/{parts[-1]}'
                        self.packages[package.name] = package
                    elif line.startswith('Depends:'):
                        assert package is not None
                        deps = line[8:].split(',')
                        package.depends = [dep.strip() for dep in deps]
                    elif line.startswith('Version:'):
                        assert package is not None
                        package.version = line[8:].strip()

                    if package and line:
                        parts = line.split(':', maxsplit=1)
                        package.stanza[parts[0].strip()] = parts[1].strip()

            else:
                logging.warning(
                    'No package index for component %s found!', component)

    def find_package(self, package_name: str) -> Optional[Package]:
        """ Find a binary deb package. """
        if package_name in self.packages:
            return self.packages[package_name]
        else:
            return None
