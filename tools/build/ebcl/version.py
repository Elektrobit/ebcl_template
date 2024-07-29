""" Debian version helpers. """
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

        return value.epoch == self.epoch and \
            value.version == self.version and \
            value.revision == self.revision

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False

        if self._lt_epoch(other.epoch):
            return True

        if self._lt_version(other.version):
            return True

        return self._lt_revision(other.revision)

    def _lt_epoch(self, other: int) -> bool:
        return self.epoch < other

    def _lt_parts(self, a: str, b: str) -> bool:
        # split to parts
        a_parts = re.findall(r'\d+|\D+', a)
        b_parts = re.findall(r'\d+|\D+', b)

        # align length
        while len(a_parts) < len(b_parts):
            a_parts.append('0')

        while len(b_parts) < len(a_parts):
            b_parts.append('0')

        # compare parts
        for x, y in zip(a_parts, b_parts):
            if x == y:
                continue

            if x.isdigit() and not y.isdigit():
                return False
            elif y.isdigit() and not x.isdigit():
                return True
            elif x.isdigit() and y.isdigit():
                return int(x) < int(y)
            else:
                # align length
                while len(x) < len(y):
                    x += 'a'
                while len(y) < len(x):
                    y += 'a'

                # compare letters
                for u, v in zip([*x], [*y]):
                    if u == v:
                        continue

                    if u == '~':
                        return True
                    if v == '~':
                        return False

                    if u.ischar() and not v.ischar():
                        return True
                    if v.ischar() and not u.ischar():
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

        if not self.revision and other:
            return True
        elif self.revision and not other:
            return False
        else:
            assert self.revision
            assert other
            return self._lt_parts(self.revision, other)


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
        elif relation == '<<':
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


@dataclass
class VersionDepends:
    """ Debian package version dependency. """
    name: str
    package_relation: Optional[PackageRelation]
    version_relation: Optional[Version]
    version: Optional[Version]


def parse_depends(
    entry: str,
    package_relation: Optional[PackageRelation] = None
) -> Optional[list[VersionDepends]]:
    if not entry:
        return None

    result = []

    alternatives = entry.split('|')

    for package in alternatives:
        package = package.strip()

        if ' ' in package:
            parts = package.split(' ', maxsplit=1)
            name = parts[0].strip()
            v = parts[1].strip()[1:-1]
            vp = v.split(' ', maxsplit=1)
            relation = vp[0].strip()
            version = vp[1].strip()

            vd = VersionDepends(
                name,
                package_relation,
                VersionRealtion.from_str(relation),
                Version(version),

            )
            result.append(vd)

    return result
