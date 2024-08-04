#!/usr/bin/env python
""" EBcL boot generator. """
import argparse
import logging
import os
import tempfile

from pathlib import Path
from typing import Optional, Any

from ebcl.common import init_logging, bug, promo
from ebcl.common.config import load_yaml
from ebcl.common.fake import Fake
from ebcl.common.files import Files, parse_scripts, EnvironmentType
from ebcl.common.proxy import Proxy
from ebcl.common.version import VersionDepends, parse_package_config, parse_package


class BootGenerator:
    """ EBcL boot generator. """

    # config file
    config: str
    # config values
    packages: list[VersionDepends]
    files: list[dict[str, str]]
    scripts: list[dict[str, Any]]
    arch: str
    archive_name: str
    target_dir: str
    archive_path: str
    download_deps: bool
    tar: bool

    # proxy
    proxy: Proxy
    # fakeroot helper
    fake: Fake
    # files helper
    fh: Files

    def __init__(self, config_file: str):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        config = load_yaml(config_file)

        self.config = config_file
        self.files = config.get('files', [])
        self.archive_name = config.get('archive_name', 'boot.tar')
        self.download_deps = config.get('download_deps', True)
        self.tar = config.get('tar', True)

        self.scripts = parse_scripts(config.get('scripts', None))

        self.arch = config.get('arch', 'arm64')

        self.packages = parse_package_config(
            config.get('packages', []), self.arch)

        kernel = parse_package(config.get('kernel', None), self.arch)
        if kernel:
            self.packages.append(kernel)

        self.proxy = Proxy()
        self.proxy.parse_apt_repos(
            apt_repos=config.get('apt_repos', None),
            arch=self.arch,
            ebcl_version=config.get('ebcl_version', None)
        )

        logging.debug('Using apt repos: %s', self.proxy.apts)

        self.fake = Fake()
        self.fh = Files(self.fake)

    def download_deb_packages(self, package_dir: str):
        """ Download all needed deb packages. """
        (_debs, _contents, missing) = self.proxy.download_deb_packages(
            packages=self.packages,
            contents=package_dir
        )

        if missing:
            logging.critical('Not found packages: %s', missing)

    def copy_files(self, package_dir: str):
        """ Copy files to be used. """

        logging.debug('Files: %s', self.files)

        for entry in self.files:
            logging.info('Processing entry: %s', entry)

            dst = Path(self.target_dir)
            if entry['destination']:
                dst = dst / entry['destination']

            src = Path(package_dir) / entry['source']

            mode: str = entry.get('mode', '600')
            uid: int = int(entry.get('uid', '0'))
            gid: int = int(entry.get('gid', '0'))

            logging.debug('Copying files %s', src)

            self.fh.copy_file(
                src=str(src),
                dst=str(dst),
                uid=uid,
                gid=gid,
                mode=mode
            )

    def run_scripts(self):
        """ Run scripts. """
        for script in self.scripts:
            logging.info('Running script %s.', script)

            file = os.path.join(os.path.dirname(
                self.config), script['name'])

            self.fh.run_script(
                file=file,
                params=script.get('params', None),
                environment=EnvironmentType.from_str(
                    script.get('env', None))
            )

    def create_boot(self, output_path: str) -> Optional[str]:
        """ Create the boot.tar.  """

        self.target_dir = tempfile.mkdtemp()
        logging.debug('Target directory: %s', self.target_dir)

        self.fh.target_dir = self.target_dir

        package_dir = tempfile.mkdtemp()
        logging.debug('Package directory: %s', package_dir)

        output_path = os.path.abspath(output_path)
        logging.debug('Output directory: %s', output_path)
        if not os.path.isdir(output_path):
            logging.critical('Output path %s is no folder!', output_path)
            exit(1)

        logging.info('Download deb packages...')
        self.download_deb_packages(package_dir)

        # Copy files and directories specified in the files
        logging.info('Copy files...')
        self.copy_files(package_dir)

        # Remove package temporary folder
        logging.info('Remove temporary package contents...')
        self.fake.run(f'rm -rf {package_dir}', check=False)

        logging.info('Running config scripts...')
        self.run_scripts()

        if self.tar:
            # create tar archive
            logging.info('Creating tar...')

            return self.fh.pack_root_as_tarball(
                output_dir=output_path,
                archive_name=self.archive_name,
                root_dir=self.target_dir,
                use_fake_chroot=False
            )
        else:
            # copy to output folder
            logging.info('Copying files...')
            files = self.fh.copy_file(f'{self.target_dir}/*',
                                      output_path,
                                      move=True,
                                      delete_if_exists=True)
            if files:
                return output_path
            else:
                logging.error(
                    'Build faild, no files found in %s.', self.target_dir)

        return None

    def finalize(self):
        """ Finalize output and cleanup. """

        # delete temporary folder
        logging.debug('Remove temporary folder...')
        self.fake.run(f'rm -rf {self.target_dir}', check=False)


def main() -> None:
    """ Main entrypoint of EBcL boot generator. """
    init_logging()

    parser = argparse.ArgumentParser(
        description='Create the content of the boot partiton as boot.tar.')
    parser.add_argument('config_file', type=str,
                        help='Path to the YAML configuration file')
    parser.add_argument('output', type=str,
                        help='Path to the output directory')

    args = parser.parse_args()

    logging.debug('Running boot_generator with args %s', args)

    # Read configuration
    generator = BootGenerator(args.config_file)

    image = None
    try:
        # Create the boot.tar
        image = generator.create_boot(args.output)
    except Exception as e:
        logging.critical('Boot build failed with exception: %s', e)
        bug()

    try:
        generator.finalize()
    except Exception as e:
        logging.error('Cleanup failed with exception! %s', e)
        bug()

    if image:
        print('Image was written to %s.', image)
        promo()
    else:
        exit(1)


if __name__ == '__main__':
    main()
