"""" EBcL deb package cache. """
import json
import logging
import os

from pathlib import Path
from typing import Optional


class Cache:
    """" EBcL deb package cache. """
    # cache folder
    folder: Path
    index_file: Path
    # index[arch][name][version] = deb_file
    index: dict[str, dict[str, dict[str, str]]]

    def __init__(self, folder: str = '/workspace/state/cache'):
        """ Setup the cache store. """
        self.folder = Path(folder)

        if not os.path.exists(self.folder):
            os.makedirs(self.folder, exist_ok=True)

        self.index_file = Path(self.folder) / 'index.json'

        if os.path.isfile(self.index_file):
            with open(self.index_file, encoding='utf8') as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def __del__(self):
        """ Save the index on destruction. """
        self.save()

    def save(self):
        """ Save the cached packages as json. """
        with open(self.index_file, 'w+', encoding='utf8') as f:
            json.dump(self.index, f)

    def add(self, arch: str, name: str, version: str, deb: str):
        """ Add a deb file to the cache. """
        if arch not in self.index:
            self.index[arch] = {}

        if name not in self.index[arch]:
            self.index[arch][name] = {}

        if version in self.index[arch][name]:
            logging.warning('Overwriting package %s.', deb)

        self.index[arch][name][version] = deb

    def get(self, arch: str, name: str, version: Optional[str] = None) -> Optional[str]:
        """ Get a deb file from the cache. """
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
