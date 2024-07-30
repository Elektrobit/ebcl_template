#!/usr/bin/env python
""" EBcL boot generator. """
import argparse
import logging
import os
import shutil
import tempfile

from pathlib import Path
from typing import Any

from .apt import Apt
from .config import load_yaml
from .fake import Fake
from .proxy import Proxy
from .version import VersionDepends, parse_depends


class BootGenerator:
    """ EBcL boot generator. """
    # config file
    config: str
    # config values
    packages: list[VersionDepends]
    files: list[dict[str, str]]
    scripts: list[str]
    arch: str
    apt_repos: list[dict[str, Any]]
    archive_name: str
    target_dir: str
    archive_path: str
    download_deps: bool
    tar: bool
    # proxy
    proxy: Proxy
    # fakeroot helper
    fake: Fake

    def __init__(self, config_file: str):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        config = load_yaml(config_file)

        self.config = config_file
        self.files = config.get('files', [])
        self.scripts = config.get('scripts', [])
        self.arch = config.get('arch', 'arm64')
        self.archive_name = config.get('archive_name', 'boot.tar')
        self.apt_repos = config.get('apt_repos', None)
        self.download_deps = config.get('download_deps', True)
        self.tar = config.get('tar', True)

        self.packages = []
        packages = config.get('packages', [])
        for package in packages:
            vds = parse_depends(package, self.arch)
            if vds:
                # TODO: handle alternatives
                self.packages.append(vds[0])
            else:
                logging.error('Parsing of package %s failed!', package)

        self.proxy = Proxy()
        if self.apt_repos is None:
            self.proxy.add_apt(
                Apt(
                    url='https://linux.elektrobit.com/eb-corbos-linux/1.2',
                    distro='ebcl',
                    components=['prod', 'dev'],
                    arch=self.arch
                )
            )
        else:
            for repo in self.apt_repos:
                self.proxy.add_apt(
                    Apt(
                        url=repo['apt_repo'],
                        distro=repo['distro'],
                        components=repo['components'],
                        arch=self.arch
                    )
                )

        self.fake = Fake()

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

        logging.info('Files: %s', self.files)

        for entry in self.files:
            dst = Path(self.target_dir)
            if entry['destination']:
                dst = dst / entry['destination']
                self.fake.run(f'mkdir -p {dst}')

            src = Path(package_dir) / entry['source']

            dst_file = dst / src.name

            mode: str = entry.get('mode', '600')
            uid = entry.get('uid', '0')
            gid = entry.get('gid', '0')

            logging.info('Copying file %s to %s', src, dst_file)

            # Ensure source file exists.
            (_out, err) = self.fake.run(f'stat {src}', check=False)
            if err:
                logging.error('File %s doesn\'t exist!', src)
                continue

            glob_files = list(src.parent.glob(src.name))
            if not glob_files:
                logging.error('Pattern %s has no matches!', src)
                continue

            for glob_file in glob_files:
                logging.info('Copying glob file %s to %s.', glob_file, dst)
                if src.is_dir():
                    self.fake.run(f'cp -R {glob_file} {dst}')
                    self.fake.run(f'chmod {mode} {dst_file}')
                    self.fake.run(f'chown -R {uid}:{gid} {dst_file}')
                else:
                    self.fake.run(f'cp {glob_file} {dst}')
                    self.fake.run(f'chmod {mode} {dst_file}')
                    self.fake.run(f'chown {uid}:{gid} {dst_file}')

    def run_scripts(self):
        """ Run scripts. """
        for script in self.scripts:
            script = os.path.abspath(os.path.join(
                os.path.dirname(self.config), script))

            logging.info('Running script: %s', script)

            if not os.path.isfile(script):
                logging.error('Script %s not found!', script)
                continue

            self.fake.run(f'{script} {self.target_dir}', cwd=self.target_dir)

    def create_boot(self, output_path: str) -> None:
        """ Create the boot.tar.  """
        self.target_dir = tempfile.mkdtemp()
        logging.info('Target directory: %s', self.target_dir)

        package_dir = tempfile.mkdtemp()
        logging.info('Package directory: %s', package_dir)

        logging.info('Download deb packages...')
        self.download_deb_packages(package_dir)

        # Copy files and directories specified in the files
        logging.info('Copy files...')
        self.copy_files(package_dir)

        # Remove package temporary folder
        shutil.rmtree(package_dir)

        self.run_scripts()

        if self.tar:
            # create tar archive
            self.fake.run('tar -cvf boot.tar .', cwd=self.target_dir)
            archive = f'{self.target_dir}/boot.tar'
            archive_out = f'{output_path}/{self.archive_name}'
            self.fake.run(f'mv {archive} {archive_out}')
        else:
            # copy to output folder
            self.fake.run(
                f'cp -R {self.target_dir}/* {output_path}')

        # delete temporary folder
        shutil.rmtree(self.target_dir)


def main() -> None:
    """ Main entrypoint of EBcL boot generator. """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Create the content of the boot partiton as boot.tar.')
    parser.add_argument('config_file', type=str,
                        help='Path to the YAML configuration file')
    parser.add_argument('output', type=str,
                        help='Path to the output directory')

    args = parser.parse_args()

    # Read configuration
    generator = BootGenerator(args.config_file)

    # Create the boot.tar
    generator.create_boot(args.output)


if __name__ == '__main__':
    main()
