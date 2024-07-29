""" Deb helper funktions. """
import logging
import os
import shutil
import tarfile
import tempfile

from pathlib import Path
from typing import Optional

import requests
import unix_ar
import zstandard

from .cache import Cache


class Package:
    """ APT package information. """
    name: str
    arch: str
    version: Optional[str] = None
    file_url: Optional[str] = None
    local_file: Optional[str] = None
    depends: list[str] = []

    def __init__(self, name: str, arch: str):
        self.name = name
        self.arch = arch

    @classmethod
    def from_deb(cls, deb: str):
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

        p = cls(name, arch)

        p.version = version

        if os.path.isfile(deb):
            p.local_file = deb

        return p

    def download(
        self, location: Optional[str] = None,
        cache: Optional[Cache] = None
    ) -> Optional[str]:
        """ Download this package. """
        if self.file_url is None:
            return None

        if location is None:
            if cache is not None:
                # If no location is give, but cache, then download to cache.
                location = cache.folder
            else:
                location = '/tmp'

        # Test if package is in cache.
        if cache is not None:
            file = cache.get(self.arch, self.name, self.version)
            if file is not None and os.path.isfile(file):
                # Use package form cache.
                logging.info('Cache hit for package %s/%s/%s.',
                             self.name, self.version, self.arch)
                dst = os.path.join(location, os.path.basename(file))
                if file != dst:
                    shutil.copy(file, dst)
                return dst

        # Download package.
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

        # Add package to cache.
        if cache is not None:
            cache.add(local_filename)

        self.local_file = local_filename

        return local_filename

    def get_depends(self) -> list[str]:
        """ Get dependencies. """
        return [dep.split(' ')[0].strip() for dep in self.depends]

    def extract(self, location: Optional[str] = None) -> Optional[str]:
        """ Extract a deb archive. """
        if not self.local_file:
            return None

        if location is None:
            location = tempfile.mkdtemp()

        deb_content_location = tempfile.mkdtemp()

        # extract deb
        logging.info('Extracting deb content of %s to %s.',
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
        logging.info('Extracting data content of %s to %s.',
                     tar_file.absolute(), location)
        tar = tarfile.open(tar_file.absolute())
        tar.extractall(path=location)
        tar.close()

        shutil.rmtree(deb_content_location)

        return location
