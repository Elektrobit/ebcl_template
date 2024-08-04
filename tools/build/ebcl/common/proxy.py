#!/usr/bin/env python
""" EBcL apt proxy. """
import logging
import os
import queue
import shutil
import tempfile

from typing import Optional, Tuple, Any

import requests

from .apt import Apt
from .cache import Cache, AddOp
from .deb import Package, filter_packages
from .version import VersionDepends, VersionRealtion


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
            self.apts = []
        else:
            self.apts = apts

        if cache is None:
            self.cache = Cache()
        else:
            self.cache = cache

    def add_apt(self, apt: Apt) -> bool:
        """ Adds an apt repo to the list of apt repos. """
        if apt not in self.apts:
            logging.info('Adding %s to proxy.', apt)
            self.apts.append(apt)
            return True
        return False

    def remove_apt(self, apt: Apt) -> bool:
        """ Removes an apt repo to the list of apt repos. """
        result = apt in self.apts

        while apt in self.apts:
            logging.info('Removing %s from proxy.', apt)
            self.apts.remove(apt)

        return result

    def find_package(self, vd: VersionDepends) -> Optional[Package]:
        """ Find package. """
        # all found packages
        packages: list[Package] = []

        for apt in self.apts:
            if vd.arch == 'any' or vd.arch == 'all' or vd.arch == apt.arch:
                ps = apt.find_package(vd.name)
                if ps:
                    packages += ps
                    logging.debug('Found %s in apt repo %s %s...',
                                  ps, apt.url, apt.distro)

        if vd.version:
            packages = [p for p in packages if filter_packages(
                p, vd.version, vd.version_relation)]

        packages.sort()

        logging.debug('Found packages: %s', packages)

        if packages:
            # Return latest package
            lp = packages[-1]

            # Check if package is available in cache.
            p = self.cache.get(
                arch=lp.arch,
                name=lp.name,
                version=lp.version,
                relation=VersionRealtion.EXACT)
            if p:
                logging.info('Found %s in cache...', p)
                lp.local_file = p.local_file

            return lp

        return None

    def _download_from_cache(
        self,
        vd: VersionDepends,
        location: Optional[str] = None
    ) -> Optional[Package]:
        """ Copy package form cache. """
        if location is None:
            location = self.cache.folder

        package = self.cache.get(
            arch=vd.arch,
            name=vd.name,
            version=vd.version,
            relation=vd.version_relation
        )

        if package and package.local_file and os.path.isfile(package.local_file):
            # Use package form cache.
            logging.debug('Cache hit for package %s.', package)
            dst = os.path.join(
                location, os.path.basename(package.local_file))
            if package.local_file != dst:
                shutil.copy(package.local_file, dst)

            package.local_file = dst
            return package

        return None

    def download_version(
        self,
        vd: VersionDepends,
        location: Optional[str] = None
    ) -> Optional[Package]:
        """ Download a deb package. """
        p = self._download_from_cache(vd, location)
        if p and p.local_file \
                and os.path.isfile(p.local_file):
            # Package was found in cache.
            return p

        package = self.find_package(vd)
        if package:
            return self.download_package(vd.arch, package, vd.version_relation, location)
        return None

    def download_package(
        self,
        arch: str,
        package: Package,
        version_relation: Optional[VersionRealtion] = None,
        location: Optional[str] = None
    ) -> Optional[Package]:
        """ Download a deb package. """
        if not version_relation:
            version_relation = VersionRealtion.LARGER

        if location is None:
            location = self.cache.folder

        p = self._download_from_cache(
            VersionDepends(
                name=package.name,
                package_relation=None,
                version_relation=version_relation,
                version=package.version,
                arch=arch
            ),
            location)

        if p:
            logging.debug('Got %s for package %s from cache.', p, package)
            if p.local_file:
                logging.debug('Local file of cache package: %s', p.local_file)
                if os.path.isfile(p.local_file):
                    logging.info(
                        'Using %s of cache package %s.', p.local_file, p)
                    return p
                else:
                    logging.debug(
                        'File %s of cache package %s does not exist!', p.local_file, p)

        else:
            logging.debug('Package %s not found in cache.', package)

        if not package.file_url:
            # Find package URL.
            p = self.find_package(
                vd=VersionDepends(
                    name=package.name,
                    package_relation=None,
                    version_relation=version_relation,
                    version=package.version,
                    arch=arch
                )
            )

            if not p or not p.file_url:
                logging.error(
                    'Package download of %s failed! URL not found.', p)
                return None

            package = p

        if not package.file_url:
            return None

        # Download package.
        logging.info('Downloading package %s from %s...',
                     package, package.file_url)
        try:
            result = requests.get(
                package.file_url, allow_redirects=True, timeout=10)
        except Exception as e:
            logging.error('Downloading package %s of %s failed! %s',
                          package, package.file_url, e)
            return None

        if result.status_code != 200:
            return None

        local_filename = package.file_url.split('/')[-1]
        local_filename = os.path.join(location, local_filename)
        with open(local_filename, 'wb') as f:
            for chunk in result.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        package.local_file = local_filename

        if location == self.cache.folder:
            # Add package to cache
            logging.debug('Adding package %s to cache.', package)
            package.local_file = self.cache.add(package, AddOp.MOVE)
        else:
            logging.info(
                'Download folder is not cache folder. Copying %s to cache.', package)
            package.local_file = self.cache.add(package, AddOp.COPY)

        return package

    def download_deb_packages(
        self,
        packages: list[VersionDepends],
        extract: bool = True,
        debs: Optional[str] = None,
        contents: Optional[str] = None,
        download_depends: bool = True
    ) -> Tuple[str, Optional[str], list[str]]:
        """ Download and optionally extract the given packages and its depends. """
        # Queue for package download.
        pq: queue.Queue[list[VersionDepends]] = queue.Queue(maxsize=-1)
        # Registry of available packages.
        local_packages: dict[str, str] = {}
        # List of not found packages
        missing: list[str] = []

        # Folder for debs
        if debs is None:
            debs = tempfile.mkdtemp()
            logging.debug('Downloading to temp folder %s.', debs)

        # Folder for package content
        if extract:
            if contents is None:
                contents = tempfile.mkdtemp()
            logging.debug('Extracting to folder %s.', contents)

        for vd in packages:
            # Adding packages to download queue.
            logging.info('Adding package %s to queue.', vd)
            pq.put_nowait([vd])

        while not pq.empty():
            vds = pq.get_nowait()
            if not vds:
                # handle empty list
                continue

            # TODO: handle alternatives
            # use always first alternative only
            vd = vds[0]

            name = vd.name

            if name in local_packages:
                continue

            package = self.find_package(vd)

            if package is None:
                logging.error('The package %s was not found!', name)
                missing.append(name)
                continue

            if not package.local_file:
                package = self.download_package(
                    arch=vd.arch,
                    package=package,
                    version_relation=vd.version_relation,
                    location=debs)

            if not package or \
                    not package.local_file or \
                    not os.path.isfile(package.local_file):
                logging.error('Download of %s failed!', name)
                missing.append(name)
                continue

            if debs != os.path.dirname(package.local_file):
                shutil.copy(package.local_file, debs)

            if extract:
                package.extract(location=contents)

            local_packages[name] = package.local_file
            logging.debug('Deb file: %s', package.local_file)

            if not download_depends:
                continue

            # Add deps to queue
            for vds in package.get_depends():
                if not vds:
                    continue

                # TODO: handle alternatives
                vd = vds[0]

                name = vd.name
                if name not in local_packages:
                    logging.info(
                        'Adding dependency %s to download queue. Queue size: %d', vd, pq.qsize())
                    pq.put_nowait([vd])

        return (debs, contents, missing)

    def parse_apt_repos(
        self,
        apt_repos: Optional[list[dict[str, Any]]],
        arch: str,
        ebcl_version: Optional[str] = None
    ) -> list[Apt]:
        """ Parse and add apt repositories. """
        # TODO: test

        if not ebcl_version:
            ebcl_version = '1.2'

        result: list[Apt] = []

        if apt_repos is None:
            ebcl = Apt.ebcl_apt(arch, ebcl_version)
            result.append(ebcl)
            self.add_apt(ebcl)
        else:
            for repo in apt_repos:
                apt = Apt.from_config(repo, arch)
                if apt:
                    result.append(apt)
                    self.add_apt(apt)
                else:
                    logging.error('Invalid apt repo config: %s', repo)

        return result
