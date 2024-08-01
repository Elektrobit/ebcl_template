#!/usr/bin/env python
""" Download and extract deb packages. """
import argparse
import logging
import os
import tempfile

from typing import Optional

from .proxy import Proxy
from .version import VersionDepends


class PackageDownloader:
    """ Download and extract deb packages. """

    # proxy
    proxy: Proxy

    def __init__(self):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        self.proxy = Proxy()

    def download_packages(
        self,
        packages: str,
        output_path: Optional[str] = None,
        arch: Optional[str] = None,
        download_depends: bool = False
    ) -> None:
        """ Create the root image.  """
        if not output_path:
            output_path = tempfile.mkdtemp()
            assert output_path

        if not arch:
            arch = 'amd64'

        content_path = os.path.join(output_path, 'contents')
        os.makedirs(content_path, exist_ok=True)

        package_names = [p.strip() for p in packages.split(' ')]

        if not package_names:
            logging.error('No package names given.')
            exit(1)

        vds: list[VersionDepends] = [VersionDepends(
            name=name,
            package_relation=None,
            version_relation=None,
            version=None,
            arch=arch
        ) for name in package_names]

        (_debs, _contents, missing) = self.proxy.download_deb_packages(
            packages=vds,
            extract=True,
            debs=output_path,
            contents=content_path,
            download_depends=download_depends
        )

        if missing:
            logging.error('Not found packages: %s', missing)

        print(f'The packages were downloaded to:\n{output_path}')
        print(f'The packages were extracted to:\n{content_path}')


def main() -> None:
    """ Main entrypoint of EBcL boot generator. """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Download and extract the given packages.')
    parser.add_argument('packages', type=str,
                        help='List of packages separated by space.')
    parser.add_argument('-o', '--output', type=str,
                        help='Path to the output directory')
    parser.add_argument('-a', '--arch', type=str,
                        help='Architecture of the packages.')
    parser.add_argument('-d', '--download-depends', action='store_true',
                        help='Download all package dependencies recursive.')

    args = parser.parse_args()

    downloader = PackageDownloader()

    downloader.download_packages(
        args.packages, args.output, args.arch, args.download_depends)


if __name__ == '__main__':
    main()
