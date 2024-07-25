#!/usr/bin/python3
""" EBcL initrd generator. """
import argparse
import logging
import os
import shutil
import subprocess
import tempfile

from pathlib import Path

from ebcl.apt import Apt
from ebcl.deb import extract_archive
from jinja2 import Template
import yaml


class InitrdGenerator:
    """ EBcL initrd generator. """
    config: Path
    modules: list[str]
    modules_packages: str
    root_device: str
    devices: list[dict[str, str]]
    files: list[dict[str, str]]
    kversion: str
    arch: str
    apt_repos: list[dict[str, str | list[str]]]
    target_dir: str
    image_path: str
    apts: list[Apt]

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

        if self.apt_repos is None:
            logging.error(
                'Providing at least one apt repository is mandatory!')
            exit(-1)

        self.apts = []
        for repo in self.apt_repos:
            self.apts.append(
                Apt(
                    url=repo['apt_repo'],
                    distro=repo['distro'],
                    components=repo['components'],
                    arch=self.arch
                )
            )

    def _chroot_run(self, cmd: str):
        """ Run command in chroot target environment. """
        subprocess.run(
            f'sudo bash -c "chroot {self.target_dir} {cmd}"',
            check=True,
            shell=True
        )

    def install_busybox(self):
        """Get busybox and add it to the initrd. """
        for apt in self.apts:
            package = apt.find_package('busybox-static')
            if package is not None:
                break

        if package is None:
            logging.error('The package busybox-static was not found!')
            exit(1)

        file = package.download()
        temp_dir = extract_archive(file)

        busybox_path = os.path.join(temp_dir, 'bin', 'busybox')
        if not os.path.isfile(busybox_path):
            logging.error(
                'The busybox binary was not found in %s!', busybox_path)
            exit(1)

        initrd_bin_dir = os.path.join(self.target_dir, 'bin')

        os.makedirs(initrd_bin_dir, exist_ok=True)
        shutil.copy(busybox_path, initrd_bin_dir)
        shutil.rmtree(temp_dir)

        self._chroot_run('/bin/busybox --install -s /bin')
        self._chroot_run('ln -s /bin /sbin')
        self._chroot_run('mkdir -p /usr')
        self._chroot_run('ln -s /bin /usr/bin')
        self._chroot_run('ln -s /bin /usr/sbin')

    def download_deb_package(self, name: str) -> str:
        """Download a deb package.

        Args:
            name (str): Name of the deb package.
            dest_dir (str): Download folder.

        Returns:
            _type_ (str): Path to the downloaded package.
        """
        for apt in self.apts:
            package = apt.find_package(name)
            if package is not None:
                break

        if package is None:
            logging.error('The package %s was not found!', name)
            exit(1)

        return package.download()

    def extract_modules_from_deb(self, mods_dir: str):
        """Extract the required kernel modules from the deb package.

        Args:
            mods_dir (str): Folder containing the modules.
        """
        # Copy the specified modules to the initrd /lib/modules directory
        initrd_modules_dir = os.path.join(
            self.target_dir, 'lib', 'modules', self.kversion)
        modulesdeps = os.path.join(initrd_modules_dir, 'modules.dep')
        os.makedirs(initrd_modules_dir, exist_ok=True)

        for module in self.modules:
            module_path = os.path.join(
                mods_dir, 'lib', 'modules', self.kversion, module)

            if not os.path.isfile(module_path):
                logging.error('Module %s not found.', module)
                continue

            target_dir = os.path.dirname(
                os.path.join(initrd_modules_dir, module))
            os.makedirs(target_dir, exist_ok=True)

            shutil.copy(module_path, target_dir)

            with open(modulesdeps, 'w', encoding='utf-8') as f:
                f.write(f'{module}:\n')

    def add_devices(self):
        """ Create device files. """
        dev_dir = os.path.join(self.target_dir, 'dev')
        os.makedirs(dev_dir, exist_ok=True)
        for device in self.devices:
            device_path = os.path.join(dev_dir, device['name'])
            major = (int)(device['major'])
            minor = (int)(device['major'])
            if device['type'] == 'block':
                os.mknod(device_path, mode=0o600 | os.makedev(major, minor))
            elif device['type'] == 'char':
                os.mknod(device_path, mode=0o200 | os.makedev(major, minor))
            else:
                logging.warning('Unsupported device type %s for %s',
                                device['type'], device['name'])

    def copy_files(self):
        """ Copy user-specified files in the initrd. """
        for entry in self.files:
            src = Path(os.path.abspath(os.path.join(
                self.config.parent, entry['source'])))
            dst = Path(self.target_dir) / entry['destination']
            mode: str = entry['mode'] if 'mode' in entry else "0o666"
            if src.is_file():
                os.makedirs(dst.parent, exist_ok=True)
                shutil.copy(src, dst)
                os.chmod(dst / src, int(mode, base=8))
            elif src.is_dir():
                if not os.listdir(src):
                    os.makedirs(dst / src, exist_ok=True)
                shutil.copytree(src, dst, dirs_exist_ok=True)
                os.chmod(dst / src, int(mode, base=8))
            else:
                logging.warning('Source %s does not exist', src)

    def create_initrd(self, image_path: str) -> None:
        """ Create the initrd image.  """
        self.target_dir = tempfile.mkdtemp()

        # Create necessary directories
        for dir_name in ['proc', 'sys', 'dev', 'sysroot', 'var',
                         'tmp', 'run', 'root', 'usr', 'sbin', 'lib', 'etc']:
            os.makedirs(Path(self.target_dir) / dir_name, exist_ok=True)

        self.install_busybox()

        mods_dir = tempfile.mkdtemp()

        for mod_package in self.modules_packages:
            deb_file = self.download_deb_package(mod_package)
            extract_archive(deb_file, location=mods_dir)
            # Remove downloaded package
            os.remove(deb_file)

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

        with open(os.path.join(os.path.dirname(__file__), 'init.sh'), encoding='utf8') as f:
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
            find_proc = subprocess.Popen(
                ['find', '.', '-print0'], cwd=self.target_dir, stdout=subprocess.PIPE)
            subprocess.run(['cpio', '--null', '-ov', '--format=newc'],
                           cwd=self.target_dir, stdin=find_proc.stdout, stdout=img,
                           check=True)

        # delete temporary folder
        shutil.rmtree(self.target_dir)


def main() -> None:
    """ Main entrypoint of EBcL initrd generator. """
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
