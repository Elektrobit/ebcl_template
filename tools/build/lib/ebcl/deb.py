""" Deb helper funktions. """
import logging
import queue
import shutil
import tarfile
import tempfile

from pathlib import Path
from typing import Optional, Tuple

import unix_ar
import zstandard

from ebcl.apt import Apt
from ebcl.cache import Cache


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
    apts: list[Apt],
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
