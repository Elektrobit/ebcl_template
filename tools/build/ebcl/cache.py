"""" EBcL deb package cache. """
import glob
import json
import logging
import os
import shutil

from enum import Enum
from typing import Optional

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
    # index[arch][name][epoch][version] = deb_file
    index: dict[str, dict[str, dict[int, dict[str, str]]]]

    def __init__(self, folder: str = '/workspace/state/cache'):
        """ Setup the cache store. """
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        assert os.path.isdir(self.folder)

        self.index_file = os.path.join(self.folder, 'index.json')

        if os.path.isfile(self.index_file):
            with open(self.index_file, encoding='utf8') as f:
                self.index = json.load(f)

            invalids: dict[str, int] = {}

            for arch in self.index.keys():
                for name in self.index[arch].keys():
                    for epoch in self.index[arch][name].keys():
                        for version in self.index[arch][name][epoch].keys():
                            deb = self.index[arch][name][epoch][version]
                            if not os.path.isfile(deb):
                                invalids[deb] = epoch

            for deb, epoch in invalids.items():
                p = Package.from_deb(deb)
                logging.info(
                    'Removing invalid deb %s from cache.', deb)
                del self.index[p.arch][p.name][epoch][p.version.version_for_filename()]
        else:
            self.index = {}

        debs = glob.glob(f'{os.path.abspath(self.folder)}/*/*.deb')
        for deb in debs:
            p = Package.from_deb(deb)
            if not self.contains(p):
                self.add(p, op=AddOp.NONE)

    def contains(self, p: Package) -> bool:
        """ Tests if the package is in the cache. """
        if not p.version:
            return False

        if p.arch in self.index:
            if p.name in self.index[p.arch]:
                if p.version.epoch in self.index[p.arch][p.name]:
                    version = p.version.version_for_filename()
                    if version in self.index[p.arch][p.name][p.version.epoch]:
                        file = self.index[p.arch][p.name][p.version.epoch][version]
                        if os.path.isfile(file):
                            return True
        return False

    def save(self):
        """ Save the cached packages as json. """
        with open(self.index_file, 'w', encoding='utf8') as f:
            json.dump(self.index, f)

    def add(self, package: Package, op: AddOp = AddOp.NONE) -> Optional[str]:
        """ Add a package to the cache. """
        logging.info('Add package %s to cache.', package)

        if not package.version:
            logging.warning(
                'Package %s has no valid version (%s)!', package, package.version)
            return None

        if not package.local_file or not os.path.isfile(package.local_file):
            logging.warning('Package %s has no valid local file!', package)
            return None

        name = package.name
        arch = package.arch
        deb_name = os.path.basename(package.local_file)

        epoch = package.version.epoch
        version = package.version.version_for_filename()

        expected_name = f'{package.name}_{version}_{package.arch}.deb'
        if deb_name != expected_name:
            logging.warning(
                'Deb %s is not following naming standards.', deb_name)

        if arch not in self.index:
            self.index[arch] = {}

        if name not in self.index[arch]:
            self.index[arch][name] = {}

        if epoch not in self.index[arch][name]:
            self.index[arch][name][epoch] = {}

        if version in self.index[arch][name][epoch]:
            logging.warning('Overwriting package %s.', package)

        local_file = package.local_file

        self.index[arch][name][epoch][version] = local_file

        dst = os.path.join(
            self.folder, f'{epoch}', os.path.basename(local_file))

        if op == AddOp.NONE:
            logging.info('Reusing existing file %s for package %s',
                         local_file, package)

        if local_file != dst and op == AddOp.MOVE or op == AddOp.COPY:
            if version in self.index[arch][name][epoch]:
                old_deb = self.index[arch][name][epoch][version]
                if os.path.isfile(old_deb):
                    logging.warning('Overwriting deb %s.', old_deb)

            elif op == AddOp.COPY:
                os.makedirs(dst, exist_ok=True)
                shutil.copy(local_file, dst)
                package.local_file = dst
                local_file = dst

            elif op == AddOp.MOVE:
                os.makedirs(dst, exist_ok=True)
                shutil.move(local_file, dst)
                package.local_file = dst
                local_file = dst

        package.local_file = local_file

        self.save()

        return local_file

    def get(
        self,
        arch: str,
        name: str,
        version: Optional[Version] = None,
        relation: Optional[VersionRealtion] = None,
    ) -> Optional[Package]:
        """ Get a deb file from the cache. """
        logging.info('Get package %s/%s/%s from cache.', name, version, arch)

        if not arch in self.index:
            return None

        if not name in self.index[arch]:
            return None

        # Get cached packages
        packages: list[Package] = []
        for epoch in self.index[arch][name]:
            for package_version in self.index[arch][name][epoch].keys():
                deb = self.index[arch][name][epoch][package_version]
                p = Package.from_deb(deb)
                if p:
                    p.version.epoch = int(epoch)
                    packages.append(p)
                else:
                    logging.warning('Removing invalid deb %s from cache.', deb)
                    del self.index[arch][name][epoch][package_version]

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
