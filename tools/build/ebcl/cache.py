"""" EBcL deb package cache. """
import json
import logging
import os

from typing import Optional


class Cache:
    """" EBcL deb package cache. """
    # cache folder
    folder: str
    index_file: str
    # index[arch][name][version] = deb_file
    index: dict[str, dict[str, dict[str, str]]]

    def __init__(self, folder: str = '/workspace/state/cache'):
        """ Setup the cache store. """
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        assert os.path.isdir(self.folder)

        self.index_file = os.path.join(self.folder, 'index.json')

        if os.path.isfile(self.index_file):
            with open(self.index_file, encoding='utf8') as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def save(self):
        """ Save the cached packages as json. """
        with open(self.index_file, 'w', encoding='utf8') as f:
            json.dump(self.index, f)

    def add(self, deb: str) -> bool:
        """ Add a deb file to the cache. """
        logging.info('Add package %s to cache.', deb)

        if not deb.endswith('.deb'):
            logging.warning('%s has no valid name extension!', deb)
            return False

        filename = os.path.basename(deb)
        filename = filename[:-4]
        parts = filename.split('_')

        if len(parts) != 3:
            logging.warning('%s is not a valid package name!', deb)
            return False

        name = parts[0]
        version = parts[1]
        arch = parts[2]

        if arch not in self.index:
            self.index[arch] = {}

        if name not in self.index[arch]:
            self.index[arch][name] = {}

        if version in self.index[arch][name]:
            logging.warning('Overwriting package %s.', deb)

        self.index[arch][name][version] = deb

        self.save()

        return True

    def get(self, arch: str, name: str, version: Optional[str] = None) -> Optional[str]:
        """ Get a deb file from the cache. """
        logging.info('Get package %s/%s/%s from cache.', name, version, arch)

        if not arch in self.index:
            return None

        if not name in self.index[arch]:
            return None

        if version is None:
            # return an arbitrary version
            return next(iter(self.index[arch][name].values()))
        elif version in self.index[arch][name]:
            return self.index[arch][name][version]
        else:
            return None
