"""" EBcL deb package cache. """
import logging
import os
import shutil

from enum import Enum
from typing import Optional

import jsonpickle

from .deb import Package, filter_packages
from .version import Version, VersionRealtion


class AddOp(Enum):
    """ File operation when package is added. """
    NONE = 1
    MOVE = 2
    COPY = 3


class Cache:
    """" EBcL deb package cache. """
    # cache folder
    folder: str
    index_file: str
    index: list[Package]

    def __init__(self, folder: str = '/workspace/state/cache'):
        """ Setup the cache store. """
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        assert os.path.isdir(self.folder)

        self.index_file = os.path.join(self.folder, 'index.json')

        if os.path.isfile(self.index_file):
            with open(self.index_file, encoding='utf8') as f:
                data = f.read()
                self.index = jsonpickle.decode(data)
        else:
            self.index = []

    def contains(self, p: Package) -> bool:
        """ Tests if the package is in the cache. """
        if not p.version:
            return False

        return p in self.index

    def save(self):
        """ Save the cached packages as json. """
        with open(self.index_file, 'w', encoding='utf8') as f:
            data = jsonpickle.encode(self.index)
            f.write(data)

    def add(self, package: Package, op: AddOp = AddOp.NONE) -> Optional[str]:
        """ Add a package to the cache. """
        logging.debug('Add package %s to cache.', package)

        if not package.version:
            logging.warning(
                'Package %s has no valid version (%s)!', package, package.version)
            return None

        if not package.local_file or not os.path.isfile(package.local_file):
            logging.warning('Package %s has no valid local file!', package)
            return None

        self.index.append(package)

        dst_folder = os.path.join(self.folder, str(package.version.epoch))
        dst_file = os.path.join(
            dst_folder, os.path.basename(package.local_file))

        if package.local_file != dst_file and op == AddOp.MOVE or op == AddOp.COPY:
            if os.path.isfile(dst_file):
                logging.warning('Overwriting deb %s.', dst_file)

            elif op == AddOp.COPY:
                os.makedirs(dst_folder, exist_ok=True)
                shutil.copy(package.local_file, dst_file)
                package.local_file = dst_file

            elif op == AddOp.MOVE:
                os.makedirs(dst_folder, exist_ok=True)
                shutil.move(package.local_file, dst_file)
                package.local_file = dst_file

        self.save()

        return package.local_file

    def get(
        self,
        arch: str,
        name: str,
        version: Optional[Version] = None,
        relation: Optional[VersionRealtion] = None,
    ) -> Optional[Package]:
        """ Get a deb file from the cache. """
        logging.debug('Get package %s/%s/%s from cache.', name, version, arch)

        packages = [p for p in self.index if p.name == name and p.arch == arch]

        if version is not None:
            if relation is None:
                relation = VersionRealtion.LARGER
            packages = [p for p in packages if filter_packages(
                p, version, relation)]

        packages.sort()

        if len(packages) > 0:
            return packages[-1]
        return None

    def __str__(self) -> str:
        return f'Cache<{self.folder}>'

    def __repr__(self) -> str:
        return self.__str__()
