#!/usr/bin/python3
""" EBcL initrd generator. """
import argparse
import logging
import os
import shutil
import subprocess
import tempfile

from pathlib import Path

import yaml
import ebcl


class InitrdGenerator:
    """ EBcL initrd generator. """
    modules: list[str]
    modules_packages: str
    root_device: str
    devices: list[dict[str, str]]
    files: list[dict[str, str]]
    kversion: str
    arch: str
    apt_repo: str
    distro: str
    components: list[str]
    target_dir: str
    image_path: str

    def __init__(self, config_file: str):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        self.modules = config.get('modules', [])
        self.modules_packages = config.get('modules_packages', '')
        self.root_device = config.get('root_device', '')
        self.devices = config.get('devices', [])
        self.files = config.get('files', [])
        self.kversion = config.get('kversion', '')
        self.arch = config.get('arch', 'arm64')
        self.apt_repo = config.get(
            'apt_repo', 'https://linux.elektrobit.com/eb-corbos-linux/1.2')
        self.distro = config.get('distro', 'ebcl')
        self.components = config.get('components', ['prod', 'dev'])

        if not self.root_device:
            logging.error('The root_device is mandatory. Please specify it.')
            exit(-1)

    def install_busybox(self):
        """Get busybox and add it to the initrd. """
        apt = ebcl.apt.Apt(
            url=self.apt_repo,
            distro=self.distro,
            components=self.components,
            arch=self.arch
        )

        package = apt.find_package('busybox-static')

        if package is None:
            logging.error('The package busybox-static was not found!')
            exit(1)

        file = package.download()
        temp_dir = ebcl.deb.extract_archive(file)

        busybox_path = os.path.join(temp_dir, 'bin', 'busybox')
        if not os.path.isfile(busybox_path):
            logging.error(
                'The busybox binary was not found in %s!', busybox_path)
            exit(1)

        initrd_bin_dir = os.path.join(self.target_dir, 'bin')
        initrd_sh_path = os.path.join(initrd_bin_dir, 'sh')

        os.makedirs(initrd_bin_dir, exist_ok=True)
        shutil.copy(busybox_path, initrd_bin_dir)
        shutil.rmtree(temp_dir)
        os.symlink('busybox', initrd_sh_path)

    def download_deb_package(self, name: str) -> str:
        """Download a deb package.

        Args:
            name (str): Name of the deb package.
            dest_dir (str): Download folder.

        Returns:
            _type_ (str): Path to the downloaded package.
        """
        apt = ebcl.apt.Apt(
            url='https://linux.elektrobit.com/eb-corbos-linux/1.2',
            distro='ebcl',
            components=['prod', 'dev'],
            arch=self.arch
        )

        package = apt.find_package(name)

        if package is None:
            logging.error('The package %s was not found!', name)
            exit(1)

        return package.download()

    def extract_modules_from_deb(self, deb_file: str):
        """Extract the required kernel modules from the deb package.

        Args:
            deb_file (str): Path to the deb archive.
        """
        temp_dir = ebcl.deb.extract_archive(deb_file)

        # Copy the specified modules to the initrd /lib/modules directory
        initrd_modules_dir = os.path.join(
            self.target_dir, 'lib', 'modules', self.kversion)
        modulesdeps = os.path.join(initrd_modules_dir, 'modules.dep')
        os.makedirs(initrd_modules_dir, exist_ok=True)

        for module in self.modules:
            module_path = os.path.join(
                temp_dir, 'lib', 'modules', self.kversion)
            if os.path.isdir(module_path):
                target_dir = os.path.join(initrd_modules_dir, module)
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy(module_path, target_dir)
                with open(modulesdeps, 'w', encoding='utf-8') as f:
                    f.write(f'{module}:\n')
            else:
                logging.warning(
                    'Module %s not found in package %s.', module, os.path.basename(deb_file))

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
            src = Path(entry['source'])
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

        for mod_package in self.modules_packages:
            deb_file = self.download_deb_package(mod_package)
            # Extract modules directly to the initrd /lib/modules directory
            self.extract_modules_from_deb(deb_file)
            # Remove downloaded package and temporary folder
            shutil.rmtree(os.path.dirname(deb_file))

        # Add device nodes
        self.add_devices()

        # Copy files and directories specified in the files
        self.copy_files()

        mods = []
        for m in self.modules:
            mods.append(m.split("/")[-1])
        modulesp: str = "\n".join(
            [f"modprobe {module}" for module in mods])
        # Create init script
        init_script: Path = Path(self.target_dir) / 'init'
        init_script_content: str = f"""#!/bin/sh

/bin/busybox --install -s /bin/
/bin/busybox --install -s /sbin/

mkdir -p /usr

ln -s /bin /usr/bin
ln -s /sbin /usr/sbin

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev

# Load kernel modules
{modulesp}


# Mount root filesystem
mount {self.root_device} /sysroot

# Switch to the new root filesystem
exec switch_root /sysroot /sbin/init
"""
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
