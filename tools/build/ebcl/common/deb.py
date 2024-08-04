""" Deb helper funktions. """
import logging
import os
import shutil
import tarfile
import tempfile

from pathlib import Path
from typing import Optional

import unix_ar
import zstandard

from .version import Version, VersionDepends, VersionRealtion


class Package:
    """ APT package information. """

    name: str
    arch: str
    repo: str
    version: Optional[Version] = None
    file_url: Optional[str] = None
    local_file: Optional[str] = None

    pre_depends: list[list[VersionDepends]] = []
    depends: list[list[VersionDepends]] = []

    breaks: list[list[VersionDepends]] = []
    conflicts: list[list[VersionDepends]] = []

    recommends: list[list[VersionDepends]] = []
    suggests: list[list[VersionDepends]] = []
    enhances: list[list[VersionDepends]] = []

    @classmethod
    def from_deb(cls, deb: str, depends: list[list[VersionDepends]]):
        """ Create a package form a deb file. """
        if not deb.endswith('.deb'):
            return None

        filename = os.path.basename(deb)[:-4]
        parts = filename.split('_')

        if len(parts) != 3:
            return None

        name = parts[0].strip()
        version = parts[1].strip()
        arch = parts[2].strip()

        p = cls(name, arch, 'local_deb')

        p.version = Version(version)
        p.depends = depends

        if os.path.isfile(deb):
            p.local_file = deb

        return p

    def __init__(self, name: str, arch: str, repo: str):
        self.name = name
        self.arch = arch
        self.repo = repo

    def get_depends(self) -> list[list[VersionDepends]]:
        """ Get dependencies. """
        return self.depends + self.pre_depends

    def extract(self, location: Optional[str] = None) -> Optional[str]:
        """ Extract a deb archive. """
        if not self.local_file:
            return None

        if not os.path.isfile(self.local_file):
            logging.error('Deb %s of package %s does not exist!',
                          self.local_file, self)
            return None

        if location is None:
            location = tempfile.mkdtemp()

        deb_content_location = tempfile.mkdtemp()

        # extract deb
        logging.debug('Extracting deb content of %s to %s.',
                      self.name, deb_content_location)
        file = unix_ar.open(self.local_file)
        file.extractall(deb_content_location)

        # find data.tar
        tar_file = Path(deb_content_location).glob('data.tar.*').__next__()
        assert tar_file is not None

        # decompress zstd file
        if tar_file.name.endswith('.zst'):
            with open(tar_file, 'rb') as compressed:
                decomp = zstandard.ZstdDecompressor()
                output_path = Path(location) / 'data.tar'
                with open(output_path, 'wb') as destination:
                    decomp.copy_stream(compressed, destination)
            tar_file = output_path

        # extract data.tar
        logging.debug('Extracting data content of %s to %s.',
                      tar_file.absolute(), location)
        tar = tarfile.open(tar_file.absolute())
        tar.extractall(path=location)
        tar.close()

        shutil.rmtree(deb_content_location)

        return location

    def __str__(self) -> str:
        return f'{self.name}:{self.arch} ({self.version})'

    def __repr__(self) -> str:
        return f'Package<{self.__str__()}>'

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Package):
            return False

        return self.arch == o.arch and \
            self.name == o.name and \
            self.version == o.version

    def __lt__(self, o: object) -> bool:
        if not isinstance(o, Package):
            return False

        if self.name != o.name:
            return self.name < o.name

        # Use package with existing local file.
        if self.version is None and o.version is None:
            if self.local_file and os.path.isfile(self.local_file):
                return False
            return True

        if self.version is None:
            return True
        if o.version is None:
            return False

        if self.version == o.version:
            # Use package with existing local file.
            if self.version is None and o.version is None:
                if self.local_file and os.path.isfile(self.local_file):
                    return False
                return True

        return self.version < o.version

    def __le__(self, o: object) -> bool:
        if not isinstance(o, Package):
            return False

        if self == o:
            return True

        return self < o


def filter_packages(p: Package, v: Version, r: Optional[VersionRealtion]) -> bool:
    """ Filter for matching packages. """
    # TODO: test
    if not p.version:
        return False

    pv = p.version

    if r == VersionRealtion.STRICT_LARGER:
        return pv > v
    elif r == VersionRealtion.LARGER:
        return pv >= v
    elif r == VersionRealtion.EXACT:
        return pv == v
    elif r == VersionRealtion.SMALLER:
        return pv <= v
    elif r == VersionRealtion.STRICT_SMALLER:
        return pv < v

    return False
