""" APT helper functions """
import gzip
import logging
import lzma

from typing import Optional

import requests

from .deb import Package
from .version import parse_depends, VersionDepends, PackageRelation, Version


class Apt:
    """ Get packages from apt repositories. """

    url: str
    distro: str
    components: list[str]
    arch: str
    packages: Optional[dict[str, list[Package]]]
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
        if self.packages is None:
            self.packages = {}

        inrelease = f'{self.url}/dists/{self.distro}/InRelease'
        try:
            response = requests.get(
                inrelease, allow_redirects=True, timeout=10)
        except Exception as e:
            logging.error('Loading index of %s failed! %s', self, e)
            return

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

                try:
                    response = requests.get(
                        packages, allow_redirects=True, timeout=10)
                except Exception as e:
                    logging.error(
                        'Loading component %s of %s failed! %s', component, self, e)
                    continue

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

            else:
                logging.warning(
                    'No package index for component %s found!', component)

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
        return f'Apt<{self.url}, {self.distro}, {self.components}>'

    def __repr__(self) -> str:
        return self.__str__()
