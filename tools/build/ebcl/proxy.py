#!/usr/bin/env python
""" EBcL apt proxy. """
import logging
import os
import queue
import tempfile

from typing import Optional, Tuple

from .apt import Apt
from .cache import Cache
from .deb import Package


class Proxy:
    """ EBcL apt proxy. """

    apts: list[Apt]
    cache: Cache

    def __init__(
        self,
        apts: Optional[list[Apt]] = None,
        cache: Optional[Cache] = None
    ) -> None:
        if apts is None:
            self.apts = [Apt()]
        else:
            self.apts = apts

        if cache is None:
            self.cache = Cache()
        else:
            self.cache = cache

    def add_apt(self, apt: Apt) -> bool:
        """ Adds an apt repo to the list of apt repos. """
        if apt not in self.apts:
            self.apts.append(apt)
            return True
        return False

    def remove_apt(self, apt: Apt) -> bool:
        """ Removes an apt repo to the list of apt repos. """
        result = apt in self.apts

        while apt in self.apts:
            self.apts.remove(apt)

        return result

    def find_package(self, arch: str, name: str) -> Optional[Package]:
        """ Find package. """
        package = None

        deb_file = self.cache.get(arch=arch, name=name)
        if deb_file and os.path.isfile(deb_file):
            package = Package.from_deb(deb_file)

        if not package:
            for apt in self.apts:
                if apt.arch == arch:
                    package = apt.find_package(name)
                    if package:
                        logging.info('Using %s from apt repo %s %s...',
                                     name, apt.url, apt.distro)
                        break
        else:
            logging.info('Using %s from cache...', deb_file)

        return package

    def download_deb_packages(
        self,
        arch: str,
        packages: list[str],
        extract: bool = True,
        debs: Optional[str] = None,
        contents: Optional[str] = None,
    ) -> Tuple[str, Optional[str], list[str]]:
        """ Download and optionally extract the given packages and its depends. """
        # Queue for package download.
        pq: queue.Queue[str] = queue.Queue(maxsize=len(packages) * 10)
        # Registry of available packages.
        local_packages: dict[str, str] = {}
        # List of not found packages
        missing: list[str] = []

        # Folder for debs
        if debs is None:
            logging.info('Downloading to cache folder %s.', self.cache.folder)
            debs = self.cache.folder

        # Folder for package content
        if extract:
            if contents is None:
                contents = tempfile.mkdtemp()
            logging.info('Extracting to folder %s.', contents)

        for p in packages:
            # Adding packages to download queue.
            logging.info('Adding package %s to queue.', p)
            pq.put_nowait(p)

        while not pq.empty():
            name = pq.get_nowait()

            if name in local_packages:
                continue

            package = self.find_package(arch, name)

            if package is None:
                logging.error('The package %s was not found!', name)
                missing.append(name)
                continue

            if not package.local_file:
                package.download(location=debs)

            if not package.local_file:
                logging.error('Download of %s failed!', name)
                missing.append(name)
                continue

            if extract:
                package.extract(location=contents)

            local_packages[name] = package.local_file
            logging.info('Deb file: %s', package.local_file)

            # Add deps to queue
            for p in package.get_depends():
                if p not in local_packages:
                    logging.info(
                        'Adding package %s to download queue. Len: %d', p, pq.qsize())
                    pq.put_nowait(p)

        return (debs, contents, missing)
