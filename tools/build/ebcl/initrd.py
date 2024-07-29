#!/usr/bin/env python
""" EBcL initrd generator. """
import argparse
import logging
import os
import shutil
import tempfile

from io import BufferedWriter
from pathlib import Path
from typing import Tuple, Any, Optional

import yaml

from jinja2 import Template

from .apt import Apt
from .fake import Fake
from .proxy import Proxy


class InitrdGenerator:
    """ EBcL initrd generator. """
    # config file
    config: Path
    # config values
    modules: list[str]
    modules_packages: str
    root_device: str
    devices: list[dict[str, str]]
    files: list[dict[str, Any]]
    kversion: str
    arch: str
    apt_repos: list[dict[str, Any]]
    template: Optional[str]
    # use fakeroot or sudo
    fakeroot: bool
    # name of busybox package
    busybox: str
    # out and tmp folders
    target_dir: str
    image_path: str
    # proxy
    proxy: Proxy
    # fakeroot helper
    fake: Fake

    def __init__(self, config_file: str):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.config = Path(config_file)

        self.modules = config.get('modules', [])
        self.modules_packages = config.get('modules_packages', '')
        self.root_device = config.get('root_device', '')
        self.devices = config.get('devices', [])
        self.files = config.get('files', [])
        self.kversion = config.get('kversion', '')
        self.arch = config.get('arch', 'arm64')
        self.apt_repos = config.get('apt_repos', None)
        self.template = config.get('template', None)
        self.fakeroot = config.get('fakeroot', False)
        self.busybox = config.get('busybox', 'busybox-static')

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

    def _run_chroot(self, cmd: str) -> Tuple[str, str]:
        """ Run command in chroot target environment. """
        if self.fakeroot:
            return self.fake.run_chroot(cmd, self.target_dir)
        else:
            return self.fake.run_sudo_chroot(cmd, self.target_dir)

    def _run_root(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        stdout: Optional[BufferedWriter] = None,
        check=True
    ) -> Tuple[Optional[str], str]:
        """ Run command as root. """
        if self.fakeroot:
            return self.fake.run(cmd=cmd, cwd=cwd, stdout=stdout, check=check)
        else:
            return self.fake.run_sudo(cmd=cmd, cwd=cwd, stdout=stdout, check=check)

    def install_busybox(self):
        """Get busybox and add it to the initrd. """
        package = self.proxy.find_package(self.arch, self.busybox)

        if package is None:
            logging.error('The package %s was not found!', self.busybox)
            exit(1)

        file = package.download()

        assert file is not None

        package.extract(self.target_dir)

        self._run_chroot('/bin/busybox --install -s /bin')

    def extract_modules_from_deb(self, mods_dir: str):
        """Extract the required kernel modules from the deb package.

        Args:
            mods_dir (str): Folder containing the modules.
        """
        initrd_modules_dir = os.path.join(
            self.target_dir, 'lib', 'modules', self.kversion)
        modulesdeps = os.path.join(initrd_modules_dir, 'modules.dep')

        self._run_chroot(f'mkdir -p /lib/modules/{self.kversion}')

        for module in self.modules:
            module_path = os.path.join(
                mods_dir, 'lib', 'modules', self.kversion, module)

            if not os.path.isfile(module_path):
                logging.error('Module %s not found.', module)
                continue

            target_dir = os.path.dirname(
                os.path.join(initrd_modules_dir, module))
            self._run_root(f'mkdir -p {target_dir}')

            self._run_root(f'cp {module_path} {target_dir}')

            self._run_root(f'echo {module}: >> {modulesdeps}')

        # Fix ownership of modules
        self._run_chroot('chown -R 0:0 /lib/modules')

    def add_devices(self):
        """ Create device files. """
        self._run_chroot('mkdir -p /dev')
        for device in self.devices:
            major = (int)(device['major'])
            minor = (int)(device['major'])
            if device['type'] == 'char':
                dev_type = 'c'
                mode = '200'
            elif device['type'] == 'block':
                dev_type = 'b'
                mode = '600'
            else:
                logging.error('Unsupported device type %s for %s',
                              device['type'], device['name'])

            self._run_chroot(
                f'mknod -m {mode} /dev/{device["name"]} {dev_type} {major} {minor}')

            uid = device.get('uid', '0')
            gid = device.get('uid', '0')
            self._run_chroot(f'chown {uid}:{gid} /dev/{device["name"]}')

    def copy_files(self):
        """ Copy user-specified files in the initrd. """
        logging.debug('Files: %s', self.files)

        for entry in self.files:
            src = Path(os.path.abspath(os.path.join(
                self.config.parent, entry['source'])))
            dst = Path(self.target_dir) / entry['destination']
            dst_file = Path(self.target_dir) / entry['destination'] / src.name
            mode: str = entry.get('mode', '666')
            uid = entry.get('uid', '0')
            gid = entry.get('gid', '0')

            logging.info('Copying %s to %s.', src, dst_file)

            self._run_root(f'mkdir -p {dst}')

            if src.is_file():
                self._run_root(f'cp {src} {dst}')
                self._run_root(f'chmod {mode} {dst_file}')
                self._run_root(f'chown {uid}:{gid} {dst_file}')
            elif src.is_dir():
                self._run_root(f'cp -R  {src}/* {dst}')
                self._run_chroot(f'chmod -R {mode} {dst_file}')
                self._run_chroot(f'chown -R {uid}:{gid} {dst_file}')
            else:
                logging.warning('Source %s does not exist', src)

    def create_initrd(self, image_path: str) -> None:
        """ Create the initrd image.  """
        self.target_dir = tempfile.mkdtemp()

        logging.info('Installing busybox...')

        self.install_busybox()

        # Create necessary directories
        for dir_name in ['proc', 'sys', 'dev', 'sysroot', 'var', 'bin',
                         'tmp', 'run', 'root', 'usr', 'sbin', 'lib', 'etc']:
            self._run_chroot(f'mkdir -p {dir_name}')
            self._run_chroot(f'chown 0:0 /{dir_name}')

        mods_dir = tempfile.mkdtemp()

        for mod_package in self.modules_packages:
            package = self.proxy.find_package(self.arch, mod_package)
            if package is None:
                logging.error('Package %s not found!', mod_package)
                exit(1)

            local_deb = package.download()
            if local_deb is None:
                logging.error('Download of %s failed!', mod_package)
                exit(1)

            package.extract(location=mods_dir)

            # Remove downloaded package
            os.remove(local_deb)

        # Extract modules directly to the initrd /lib/modules directory
        self.extract_modules_from_deb(mods_dir)

        # Remove mods temporary folder
        shutil.rmtree(mods_dir)

        # Add device nodes
        self.add_devices()

        # Copy files and directories specified in the files
        self.copy_files()

        # Create init script
        init_script: Path = Path(self.target_dir) / 'init'

        if self.template is None:
            template = os.path.join(os.path.dirname(__file__), 'init.sh')
        else:
            template = os.path.join(
                os.path.dirname(self.config), self.template)

        with open(template, encoding='utf8') as f:
            tmpl = Template(f.read())

        init_script_content = tmpl.render(
            root=self.root_device,
            mods=[m.split("/")[-1] for m in self.modules]
        )

        init_script.write_text(init_script_content)
        os.chmod(init_script, 0o755)

        # Create initrd image
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as img:
            self._run_root(
                'find . -print0 | cpio --null -ov --format=newc', cwd=self.target_dir, stdout=img)

        # delete temporary folder
        self._run_root(f' rm -rf {self.target_dir}')


def main() -> None:
    """ Main entrypoint of EBcL initrd generator. """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Create an initrd image for Linux.')
    parser.add_argument('config_file', type=str,
                        help='Path to the YAML configuration file')
    parser.add_argument('output', type=str,
                        help='Path to the output directory')

    args = parser.parse_args()

    # Read configuration
    generator = InitrdGenerator(args.config_file)

    # Define output image path
    output_image_path = os.path.join(args.output, 'initrd.img')

    # Create initrd image with modules extracted from the Debian package
    generator.create_initrd(output_image_path)


if __name__ == '__main__':
    main()
