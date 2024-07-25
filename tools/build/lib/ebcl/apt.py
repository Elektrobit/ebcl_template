""" APT helper functions """
import gzip
import logging
import lzma
import tarfile
import os

from dataclasses import dataclass
from typing import Dict

import requests


@dataclass
class Package:
    """ APT package information. """
    name: str
    file_url: str

    def __init__(self, name: str):
        self.name = name

    def download(self, location: str = '/tmp') -> str | None:
        """ Download this package. """
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
        return local_filename


class Apt:
    """ Get packages from apt repositories. """

    def __init__(
        self,
        url: str = "http://archive.ubuntu.com/ubuntu",
        distro: str = "jammy",
        components: [str] = None,
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
                    if line.startswith('Package:'):
                        parts = line.split(' ')
                        package = Package(parts[-1])
                    if line.startswith('Filename:'):
                        assert package is not None
                        parts = line.split(' ')
                        package.file_url = f'{self.url}/{parts[-1]}'
                        self.packages[package.name] = package
            else:
                logging.warning(
                    'No package index for component %s found!', component)

    def find_package(self, package_name: str) -> Package | None:
        """ Find a binary deb package. """
        if package_name in self.packages:
            return self.packages[package_name]
        else:
            return None
