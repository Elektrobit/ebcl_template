""" Debian version helpers. """
import logging
import re

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Version:
    """ Debian package version. """
    # Epoch of package - small unsigned int
    epoch: int
    # Upstream package version - X.Y.Z
    version: str
    # Debian revision.
    revision: Optional[str]

    def __init__(self, package_version: str):
        version = package_version.strip()

        if ':' in version:
            parts = version.split(':', maxsplit=1)
            self.epoch = int(parts[0].strip())
            version = parts[1]
        else:
            self.epoch = 0

        if '-' in version:
            parts = version.split('-')
            self.revision = parts[-1]
            version = '-'.join(parts[:-1])
        else:
            self.revision = None

        if not version:
            return None

        self.version = version

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Version):
            return False

        return int(value.epoch) == int(self.epoch) and \
            value.version == self.version and \
            value.revision == self.revision

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False

        if int(self.epoch) != int(other.epoch):
            self._lt_epoch(other.epoch)

        if self.version != other.version:
            return self._lt_version(other.version)

        return self._lt_revision(other.revision)

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False

        if self == other:
            return True

        return self < other

    def _lt_epoch(self, other: int) -> bool:
        return self.epoch < other

    def _lt_parts(self, a: str, b: str) -> bool:
        # split to parts
        a_parts = re.findall(r'\d+|\D+', a)
        b_parts = re.findall(r'\d+|\D+', b)

        # align length
        while len(a_parts) < len(b_parts):
            a_parts.append(None)

        while len(b_parts) < len(a_parts):
            b_parts.append(None)

        # compare parts
        for x, y in zip(a_parts, b_parts):
            if x == y:
                continue

            if x is None:
                return True
            if y is None:
                return False

            if x.isdigit() and not y.isdigit():
                return False
            elif y.isdigit() and not x.isdigit():
                return True
            elif x.isdigit() and y.isdigit():
                return int(x) < int(y)
            else:
                # align length
                while len(x) < len(y):
                    x += '~'
                while len(y) < len(x):
                    y += '~'

                # compare letters
                for u, v in zip([*x], [*y]):
                    if u == v:
                        continue

                    if u == '~':
                        return True
                    if v == '~':
                        return False

                    if u.isalpha() and not v.isalpha():
                        return True
                    if v.isalpha() and not u.isalpha():
                        return False

                    return u < v

        return False

    def _lt_version(self, other: str) -> bool:
        if self.version == other:
            return False

        return self._lt_parts(self.version, other)

    def _lt_revision(self, other: Optional[str]) -> bool:
        if self.version == other:
            return False

        if not self.revision and not other:
            return False
        if not self.revision:
            return True
        elif not other:
            return False
        else:
            assert other
            return self._lt_parts(self.revision, other)

    def version_for_filename(self) -> str:
        """ Get a string formatted version for the filename. """
        if self.revision:
            return f'{self.version}-{self.revision}'
        else:
            return f'{self.version}'

    def __str__(self) -> str:
        if self.revision:
            return f'{self.epoch}:{self.version}-{self.revision}'
        else:
            return f'{self.epoch}:{self.version}'

    def __repr__(self) -> str:
        return self.__str__()


class VersionRealtion(Enum):
    """ Debian package version relation. """
    STRICT_SMALLER = 1
    SMALLER = 2
    EXACT = 3
    LARGER = 4
    STRICT_LARGER = 5

    @classmethod
    def from_str(cls, relation: str):
        """ Get ImageType from str. """
        if relation == '<<':
            return cls.STRICT_SMALLER
        elif relation == '<=':
            return cls.SMALLER
        elif relation == '=':
            return cls.EXACT
        elif relation == '>=':
            return cls.LARGER
        elif relation == '>>':
            return cls.STRICT_LARGER
        else:
            return None

    def __str__(self) -> str:
        if self.value == 1:
            return '<<'
        elif self.value == 2:
            return '<='
        elif self.value == 3:
            return '='
        elif self.value == 4:
            return '>='
        elif self.value == 5:
            return '>>'
        else:
            return "UNKNOWN"

    def __repr__(self) -> str:
        return self.__str__()


class PackageRelation(Enum):
    """ Debian package relation. """
    DEPENDS = 1
    PRE_DEPENS = 2
    RECOMMENDS = 3
    SUGGESTS = 4
    ENHANCES = 5
    BREAKS = 6
    CONFLICTS = 7

    def __str__(self) -> str:
        if self.value == 1:
            return "depends"
        elif self.value == 2:
            return "pre-depends"
        elif self.value == 3:
            return "recommends"
        elif self.value == 4:
            return "suggests"
        elif self.value == 5:
            return "enhances"
        elif self.value == 7:
            return "conflicts"
        else:
            return "UNKNOWN"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class VersionDepends:
    """ Debian package version dependency. """
    name: str
    package_relation: Optional[PackageRelation]
    version_relation: Optional[VersionRealtion]
    version: Optional[Version]
    arch: str

    def __str__(self) -> str:
        t = f'VersionDepends<{self.name}'
        if self.package_relation:
            t += f', pr: {self.package_relation}'
        if self.version_relation:
            t += f', vr: {self.version_relation}'
        if self.version:
            t += f', v: {self.version}'
        if self.arch:
            t += f', arch: {self.arch}'

        return t + '>'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, VersionDepends):
            return False

        return self.name == value.name and \
            self.package_relation == value.package_relation and \
            self.version_relation == value.version_relation and \
            self.arch == value.arch

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, VersionDepends):
            return False

        if self.name == other.name:
            if self.version and other.version:
                return self.version < other.version
            elif self.version:
                return False
            else:
                return True

        return self.name < other.name

    def __le__(self, other: object) -> bool:
        if not isinstance(other, VersionDepends):
            return False

        if self == other:
            return True

        return self < other


def parse_depends(
    entry: str,
    default_arch: str,
    package_relation: Optional[PackageRelation] = None
) -> Optional[list[VersionDepends]]:
    """ Parse package depends entry. """
    if not entry:
        return None

    result = []

    alternatives = entry.split('|')

    for package in alternatives:
        package = package.strip()

        parts = package.split(' ', maxsplit=1)

        arch = default_arch
        name = parts[0].strip()
        if ':' in name:
            np = name.split(':')
            name = np[0]
            arch = np[1]

        version = None
        version_relation = None
        if len(parts) > 1:
            v = parts[1].strip()[1:-1]
            if ' ' in v:
                vp = v.split(' ', maxsplit=1)
                version_relation = VersionRealtion.from_str(vp[0].strip())
                version = Version(vp[1].strip())
            else:
                version = Version(v.strip())
                version_relation = VersionRealtion.EXACT

        vd = VersionDepends(
            name,
            package_relation,
            version_relation,
            version,
            arch
        )
        result.append(vd)

    return result


def parse_package_config(packages: list[str], arch: str) -> list[VersionDepends]:
    """ Parse packages conifguration. """
    vd_list: list[VersionDepends] = []
    for package in packages:
        vds = parse_depends(package, arch)
        if vds:
            # TODO: handle alternatives
            vd_list.append(vds[0])
        else:
            logging.error('Parsing of package %s failed!', package)

    return vd_list


def parse_package(package: Optional[str], arch: str) -> Optional[VersionDepends]:
    """ Parse a single package configuration. """
    if package:
        vds = parse_depends(package, arch)

        if vds:
            if len(vds) > 1:
                logging.warning(
                    'Found more than one package: %s. Using %s', vds, vds[0])

            logging.debug('Package: %s', vds[0])
            return vds[0]
        else:
            logging.error('Parsing of package %s failed!', package)

    return None
