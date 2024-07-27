""" Deb helper funktions. """
import logging
import os
import queue
import shutil
import tarfile
import tempfile

from pathlib import Path
from typing import Optional, Tuple, Any

import requests
import unix_ar
import zstandard

from .cache import Cache


class Package:
    """ APT package information. """
    name: str
    version: str
    arch: str
    file_url: str
    depends: list[str]

    def __init__(self, name: str):
        self.name = name
        self.depends = []

    def download(
        self, location: Optional[str] = None,
        cache: Optional[Cache] = None
    ) -> Optional[str]:
        """ Download this package. """
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

        return local_filename

    def get_depends(self) -> list[str]:
        """ Get dependencies. """
        return [dep.split(' ')[0].strip() for dep in self.depends]


def extract_archive(deb_file: str, location: Optional[str] = None) -> str:
    """ Extract a deb archive. """
    if location is None:
        location = tempfile.mkdtemp()

    deb_content_location = tempfile.mkdtemp()

    # extract deb
    file = unix_ar.open(deb_file)
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
    tar = tarfile.open(tar_file.absolute())
    data = Path(location)
    tar.extractall(path=data)
    tar.close()

    shutil.rmtree(deb_content_location)

    return location


def download_deb_packages(
    apts: list[Any],
    packages: list[str],
    debs: Optional[str] = None,
    contents: Optional[str] = None,
    cache: Optional[Cache] = None
) -> Tuple[str, str, list[str]]:
    """ Download and extract the given packages and its depends. """
    # Queue for package download.
    pq: queue.Queue[str] = queue.Queue(maxsize=len(packages) * 100)

    # Registry of available packages.
    local_packages: dict[str, str] = {}

    # List of not found packages
    missing: list[str] = []

    # Folder for debs
    if debs is None:
        if cache:
            debs = cache.folder
        else:
            debs = tempfile.mkdtemp()

    # Folder for package content
    if contents is None:
        contents = tempfile.mkdtemp()

    for p in packages:
        logging.info('Adding package %s to download queue.', p)
        pq.put_nowait(p)

    while not pq.empty():
        name = pq.get_nowait()

        for apt in apts:
            package = apt.find_package(name)
            if package is not None:
                break

        if package is None:
            logging.error('The package %s was not found!', name)
            missing.append(name)
            continue

        if name not in local_packages:
            # Download and extract deb
            logging.info('Downloading package %s...', package.name)
            deb_file = package.download(location=debs, cache=cache)

            assert deb_file is not None

            local_packages[name] = deb_file
            logging.info('Deb file: %s', deb_file)

            extract_archive(deb_file, location=contents)

            # Add deps to queue
            for p in package.get_depends():
                if p not in local_packages:
                    logging.info(
                        'Adding package %s to download queue. Len: %d', p, pq.qsize())
                    pq.put_nowait(p)

    return (debs, contents, missing)
