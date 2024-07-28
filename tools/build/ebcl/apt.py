""" APT helper functions """
import gzip
import logging
import lzma
import queue
import tempfile

from typing import Optional, Tuple

import requests

from .cache import Cache
from .deb import Package


class Apt:
    """ Get packages from apt repositories. """

    url: str
    distro: str
    components: list[str]
    arch: str
    packages: Optional[dict[str, Package]]
    index_loaded: bool

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
        self.packages = None

    def _load_index(self):
        """ Download repo metadata and parse package indices. """
        if self.packages is None:
            self.packages = {}

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
                        package = Package(parts[-1], self.arch)
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

            else:
                logging.warning(
                    'No package index for component %s found!', component)

    def find_package(self, package_name: str) -> Optional[Package]:
        """ Find a binary deb package. """
        if self.packages is None:
            self._load_index()

        assert self.packages is not None

        if package_name in self.packages:
            return self.packages[package_name]
        else:
            return None


def download_deb_packages(
    arch: str,
    apts: list[Apt],
    packages: list[str],
    debs: Optional[str] = None,
    contents: Optional[str] = None,
    cache: Optional[Cache] = None
) -> Tuple[str, str, list[str]]:
    """ Download and extract the given packages and its depends. """
    # Queue for package download.
    pq: queue.Queue[str] = queue.Queue(maxsize=len(packages) * 100)
    # Registry of available packages.
    local_packages: dict[str, str] = {}
    # List of not found packages
    missing: list[str] = []

    # Folder for debs
    if debs is None:
        if cache:
            logging.info('Downloading to cache folder %s.', cache.folder)
            debs = cache.folder
        else:
            debs = tempfile.mkdtemp()

    # Folder for package content
    if contents is None:
        contents = tempfile.mkdtemp()

    logging.info('Extracting to folder %s.', contents)

    for p in packages:
        # Adding packages to download queue.
        logging.info('Adding package %s to download queue.', p)
        pq.put_nowait(p)

    while not pq.empty():
        name = pq.get_nowait()

        if name in local_packages:
            continue

        for apt in apts:
            package = apt.find_package(name)
            if package is not None:
                break

        if package is None:
            logging.error('The package %s was not found!', name)
            missing.append(name)
            continue

        deb_file = None
        if cache:
            deb_file = cache.get(arch, name)
            if deb_file:
                logging.info('Using %s from cache.', name)
                package.local_file = deb_file

        if not deb_file:
            deb_file = package.download(location=debs, cache=cache)

        if not deb_file:
            logging.error('Download of %s failed!', name)
            missing.append(name)
            continue

        package.extract(location=contents)

        local_packages[name] = deb_file
        logging.info('Deb file: %s', deb_file)

        # Add deps to queue
        for p in package.get_depends():
            if p not in local_packages:
                logging.info(
                    'Adding package %s to download queue. Len: %d', p, pq.qsize())
                pq.put_nowait(p)

    return (debs, contents, missing)
