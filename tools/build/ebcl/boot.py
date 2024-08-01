#!/usr/bin/env python
""" EBcL boot generator. """
import argparse
import glob
import logging
import os
import tempfile

from pathlib import Path

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

        kernel = config.get('kernel', None)
        if kernel:
            vds = parse_depends(kernel, self.arch)
            if vds:
                logging.info('Kernel package: %s', vds[0])
                # TODO: handle alternatives
                self.packages.append(vds[0])
            else:
                logging.error('Parsing of kernel %s failed!', kernel)

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
            logging.info('Processing entry: %s', entry)

            dst = Path(self.target_dir)
            if entry['destination']:
                dst = dst / entry['destination']
                self.fake.run(f'mkdir -p {dst}')

            src = Path(package_dir) / entry['source']

            mode: str = entry.get('mode', '600')
            uid = entry.get('uid', '0')
            gid = entry.get('gid', '0')

            logging.info('Copying files %s', src)

            # Ensure source file exists.
            (_out, err, _returncode) = self.fake.run(
                f'stat {src}', check=False)
            if err:
                logging.error('File %s doesn\'t exist!', src)
                continue

            glob_files = list(src.parent.glob(src.name))
            if not glob_files:
                logging.error('Pattern %s has no matches!', src)
                continue

            logging.info('Glob files: %s', glob_files)

            for glob_file in glob_files:
                dst_file = dst / glob_file.name

                logging.info('Copying glob file %s to %s.',
                             glob_file, dst_file)

                self.fake.run(f'stat {glob_file}')
                self.fake.run(f'stat {dst}')
                self.fake.run(f'cp -R {glob_file} {dst_file}')
                self.fake.run(f'chmod {mode} {dst_file}')
                self.fake.run(f'chown -R {uid}:{gid} {dst_file}')

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

        output_path = os.path.abspath(output_path)
        logging.info('Output directory: %s', output_path)
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

            self.fake.run('tar -cvf boot.tar .', cwd=self.target_dir)
            archive = f'{self.target_dir}/boot.tar'
            archive_out = f'{output_path}/{self.archive_name}'

            if os.path.isfile(archive_out):
                logging.info('Deleting old archive %s...', archive_out)
                self.fake.run(f'rm -f {archive_out}', check=False)

            logging.info('Moving archive to output folder %s...', output_path)
            self.fake.run(f'mv {archive} {archive_out}')
        else:
            # copy to output folder
            files = glob.glob(f'{self.target_dir}/*')

            logging.info('Moving files %s to output folder %s...',
                         files, output_path)

            for file in files:
                dst = os.path.join(output_path, os.path.basename(file))

                logging.info('Moving file %s to %s...', file, dst)

                if os.path.exists(dst):
                    logging.info('Deleting old output file %s...', dst)
                    self.fake.run(f'rm -rf {dst}', check=False)

                self.fake.run(f'mv {file} {dst}')

        # delete temporary folder
        logging.info('Remove temporary folder...')
        self.fake.run(f'rm -rf {self.target_dir}', check=False)


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

    logging.info('Running boot_generator with args %s', args)

    # Read configuration
    generator = BootGenerator(args.config_file)

    # Create the boot.tar
    generator.create_boot(args.output)


if __name__ == '__main__':
    main()
