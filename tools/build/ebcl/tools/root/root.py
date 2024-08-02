#!/usr/bin/env python
""" EBcL root filesystem generator. """
import argparse
import glob
import logging
import os
import shutil
import tempfile

from enum import Enum
from pathlib import Path
from typing import Optional, Any
from urllib.parse import urlparse

import yaml

from jinja2 import Template

from ebcl.common.apt import Apt
from ebcl.common.config import load_yaml
from ebcl.common.fake import Fake
from ebcl.common.files import Files, EnvironmentType, parse_scripts
from ebcl.common.proxy import Proxy
from ebcl.common.version import VersionDepends, parse_package_config, parse_package


class ImageType(Enum):
    """ Enum for supported image types. """
    ELBE = 1
    KIWI = 2

    @classmethod
    def from_str(cls, image_type: str):
        """ Get ImageType from str. """
        if image_type == 'elbe':
            return cls.ELBE
        elif image_type == 'kiwi':
            return cls.KIWI
        else:
            return None

    def __str__(self) -> str:
        if self.value == 1:
            return "elbe"
        elif self.value == 2:
            return "kiwi"
        else:
            return "UNKNOWN"


class RootGenerator:
    """ EBcL root filesystem generator. """
    # config file
    config: str
    # config values
    name: str
    arch: str
    image_type: ImageType
    image: Optional[str]
    template: Optional[str]
    scripts: list[dict[str, Any]]
    apt_repos: list[Apt]
    # build result filename pattern
    result: Optional[str]
    # packages to install
    packages: list[VersionDepends]
    # root password
    root_password: str

    # sysroot
    sysroot_packages: list[VersionDepends]
    sysroot_defaults: bool
    sysroot: bool

    # kiwi specific parameters
    kvm: bool
    berrymill_conf: Optional[str]
    bootstrap_package: Optional[str]
    bootstrap: Optional[list[str]]
    use_kiwi_defaults: bool
    kiwi_scripts: list[str]
    kiwi_root_overlays: list[str]
    image_version: str

    # elbe specific parameters
    primary_repo: Optional[Apt]
    hostname: str
    domain: str
    console: str
    packer: str

    # fakeroot helper
    fake: Fake
    # proxy
    proxy: Proxy
    # files helper
    fh: Files
    # folder for script execution
    target_dir: Optional[str]
    # folder to collect build results
    result_dir: Optional[str]

    def __init__(self, config_file: str):
        """ Parse the yaml config file.

        Args:
            config_file (Path): Path to the yaml config file.
        """
        config = load_yaml(config_file)

        self.config = config_file

        self.arch = config.get('arch', 'arm64')

        self.scripts = parse_scripts(config.get('scripts', None))

        self.image = config.get('image', None)
        self.template = config.get('template', None)

        self.berrymill_conf = config.get('berrymill_conf', None)
        self.bootstrap_package = config.get('bootstrap_package', None)
        self.bootstrap = config.get('bootstrap', None)
        self.kiwi_scripts = config.get('kiwi_scripts', [])
        self.kiwi_root_overlays = config.get('kiwi_root_overlays', [])
        self.use_kiwi_defaults = config.get('use_kiwi_defaults', True)
        self.kvm = config.get('kvm', True)
        self.image_version = config.get('image_version', '1.0.0')

        self.name = config.get('name', 'root')

        self.image_type = ImageType.from_str(config.get('type', 'elbe'))
        logging.info('Using image type: %s', self.image_type)

        if self.image_type == ImageType.ELBE:
            primary_repo = config.get('primary_repo', None)
            if not primary_repo:
                if self.arch == 'amd64':
                    primary_repo = 'http://archive.ubuntu.com/ubuntu'
                else:
                    primary_repo = 'http://ports.ubuntu.com/ubuntu-ports/'

            primary_distro = config.get('primary_repo', 'jammy')

            self.primary_repo = Apt(
                url=primary_repo,
                distro=primary_distro,
                components=['main'],
                arch=self.arch
            )

        self.root_password = config.get('root_password', 'linux')

        self.hostname = config.get('hostname', 'ebcl')
        self.domain = config.get('domain', 'elektrobit.com')
        self.console = config.get('console', 'ttyAMA0,115200')
        self.packer = config.get('packer', 'none')

        self.packages = parse_package_config(
            config.get('packages', []), self.arch)

        kernel = parse_package(config.get('kernel', None), self.arch)
        if kernel:
            self.packages.append(kernel)

        self.sysroot_packages = parse_package_config(
            config.get('sysroot_packages', []), self.arch)

        self.sysroot_defaults = config.get('sysroot_defaults', True)

        self.proxy = Proxy()
        self.apt_repos = self.proxy.parse_apt_repos(
            apt_repos=config.get('apt_repos', None),
            arch=self.arch,
            ebcl_version=config.get('ebcl_version', None)
        )

        if self.primary_repo:
            self.proxy.add_apt(self.primary_repo)

        self.fake = Fake()
        self.files = Files(self.fake)

    def _run_scripts(self):
        """ Run scripts. """
        for script in self.scripts:
            logging.info('Running script: %s', script)

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

    def _generate_elbe_image(self) -> Optional[str]:
        """ Generate an elbe image description. """
        assert self.result_dir

        # TODO: test

        logging.info('Generating elbe image from template...')

        if not self.primary_repo:
            logging.critical('No primary repo!')
            return None

        if not self.packages:
            logging.critical('Packages defined!')
            return None

        params: dict[str, Any] = {}

        params['name'] = self.name
        params['arch'] = self.arch

        try:
            url = urlparse(self.primary_repo.url)
        except Exception as e:
            logging.critical(
                'Invalid primary repo url %s! %s', self.primary_repo.url, e)
            return None

        params['primary_repo_url'] = url.netloc
        params['primary_repo_path'] = url.path
        params['primary_repo_proto'] = url.scheme

        params['distro'] = self.primary_repo.distro

        params['hostname'] = self.hostname
        params['domain'] = self.domain
        params['root_password'] = self.root_password
        params['console'] = self.console

        params['packages'] = self.packages

        params['packer'] = self.packer
        params['output_archive'] = 'root.tar'

        if self.apt_repos:
            params['apt_repos'] = []
            for repo in self.apt_repos:
                components = ' '.join(repo.components)
                apt_line = f'{repo.url} {repo.distro} {components}'

                key = repo.get_key()

                if key:
                    params['apt_repos'].append({
                        'apt_line': apt_line,
                        'arch': repo.arch,
                        'key': key
                    })
                else:
                    params['apt_repos'].append({
                        'apt_line': apt_line,
                        'arch': repo.arch,
                    })

        if self.template is None:
            template = os.path.join(os.path.dirname(__file__), 'root.xml')
        else:
            template = os.path.join(
                os.path.dirname(self.config), self.template)

        with open(template, encoding='utf8') as f:
            tmpl = Template(f.read())

        template_content = tmpl.render(**params)

        image_file = os.path.join(self.result_dir, 'image.xml')
        with open(image_file, 'w', encoding='utf8') as f:
            f.write(template_content)

        logging.info('Generated image stored as %s', image_file)

        return image_file

    def _build_elbe_image(self) -> Optional[str]:
        """ Run elbe image build. """
        assert self.result_dir

        if not self.image:
            self.image = self._generate_elbe_image()

        if not self.image:
            logging.critical('No elbe image description found!')
            return None

        image = Path(os.path.join(os.path.dirname(self.config), self.image))
        if not image.is_file():
            logging.critical('Image %s not found!', image)
            return None

        (out, err, _returncode) = self.fake.run_no_fake(
            'elbe control create_project')
        assert not err
        assert out
        prj = out.strip()

        pre_xml = os.path.join(self.result_dir, image.name) + '.gz'

        self.fake.run_no_fake(
            f'elbe preprocess --output={pre_xml} {image.absolute()}', check=False)
        self.fake.run_no_fake(
            f'elbe control set_xml {prj} {pre_xml}', check=False)
        self.fake.run_no_fake(f'elbe control build {prj}')
        self.fake.run(f'elbe control wait_busy {prj}')
        self.fake.run(
            f'elbe control get_files --output {self.result_dir} {prj}')
        self.fake.run(f'elbe control del_project {prj}')

        tar = os.path.join(self.result_dir, 'root.tar')

        if os.path.isfile(tar):
            return tar

        results = Path(self.result_dir)

        # search for tar
        pattern = '*.tar'
        if self.result:
            pattern = self.result

        images = list(results.glob(pattern))
        if images:
            return os.path.join(self.result_dir, images[0])

        return None

    def _generate_kiwi_image(self) -> Optional[str]:
        """ Generate a kiwi image description. """
        assert self.result_dir

        # TODO: test

        if not self.apt_repos:
            logging.critical('No apt repositories defined!')
            return None

        bootstrap_package = self.bootstrap_package
        if len(self.apt_repos) > 1 and not bootstrap_package:
            bootstrap_package = 'bootstrap-root-ubuntu-jammy'
            logging.warning('More than one apt repository specified, '
                            'a boostrap_package is required! '
                            'Falling back to %s.')
            return None

        params: dict[str, Any] = {}

        if self.arch == 'arm64':
            params['arch'] = 'aarch64'
        else:
            params['arch'] = 'x86_64'

        params['version'] = self.image_version
        params['root_password'] = self.root_password
        params['packages'] = self.packages

        if self.bootstrap_package:
            params['bootstrap_package'] = self.bootstrap_package

        if self.bootstrap:
            params['bootstrap'] = self.bootstrap

        if self.template is None:
            template = os.path.join(os.path.dirname(__file__), 'root.kiwi')
        else:
            template = os.path.join(
                os.path.dirname(self.config), self.template)

        with open(template, encoding='utf8') as f:
            tmpl = Template(f.read())

        template_content = tmpl.render(**params)

        image_file = os.path.join(self.result_dir, 'image.xml')
        with open(image_file, 'w', encoding='utf8') as f:
            f.write(template_content)

        logging.info('Generated image stored as %s', image_file)

        return image_file

    def _generate_berrymill_config(self) -> Optional[str]:
        """ Generate a berrymill.conf. """
        assert self.result_dir

        # TODO: test

        berrymill_conf: dict[str, Any] = {}

        berrymill_conf['use-global-repos'] = False
        berrymill_conf['boxed_plugin_conf'] = '/etc/berrymill/kiwi_boxed_plugin.yml'
        berrymill_conf['repos'] = {}
        berrymill_conf['repos']['release'] = {}

        for apt in self.apt_repos:
            try:
                url = urlparse(apt.url)
            except Exception as e:
                logging.error(
                    'Invalid apt url %s, skippung repo! %s', apt.url, e)
                continue

            cmp_str = '_'.join(apt.components)
            repo_key = f'{url.netloc.replace}_{apt.distro}_{cmp_str}'

            if apt.arch not in berrymill_conf['repos']['release']:
                berrymill_conf['repos']['release'][apt.arch] = {}

            cmp_str = ','.join(apt.components)
            berrymill_conf['repos']['release'][apt.arch][repo_key] = {
                'url': apt.url,
                'type': 'apt-deb',
                'key': apt.key_url,
                'name': apt.distro,
                'components': cmp_str
            }

        config_file = os.path.join(self.result_dir, 'berrymill.conf')

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                data = yaml.dump(berrymill_conf)
                f.write(data)
        except Exception as e:
            logging.critical('Saving berrymill.conf failed! %s', e)
            return None

        return config_file

    def _copy_files(self, files: list[str], dst: str):
        """ Copy files to dst. """
        logging.info('Files: %s', files)

        for file in files:
            src = os.path.join(os.path.dirname(self.config), file)

            logging.info('Copying file %s...', file)

            logging.info('Copying files %s', src)

            self.fh.copy_file(
                src=str(src),
                dst=str(dst),
            )

    def _build_kiwi_image(self, output_path: str) -> Optional[str]:
        """ Run kiwi image build. """
        assert self.result_dir

        berrymill_conf = self.berrymill_conf
        if not berrymill_conf:
            logging.info('Generating the berrymill.conf...')
            berrymill_conf = self._generate_berrymill_config()
            if not berrymill_conf:
                logging.critical('Generating a berrymill.conf failed!')
                return None

        if not self.image:
            self.image = self._generate_kiwi_image()

        if not self.image:
            logging.critical('No kiwi image description found!')
            return None

        image = Path(os.path.join(os.path.dirname(self.config), self.image))
        if not image.is_file():
            logging.critical('Image %s not found!', image)
            return None

        logging.info('Berrymill.conf: %s', berrymill_conf)

        appliance = Path(self.result_dir) / image.name

        if appliance.absolute() != image.absolute():
            shutil.copy(image, appliance)

        kiwi_scripts = self.kiwi_scripts
        kiwi_root_overlays = self.kiwi_root_overlays

        if self.use_kiwi_defaults:
            conf_dir = Path(self.config).parent

            root_overlay = conf_dir / 'root'
            if root_overlay.is_dir():
                logging.info('Adding %s to kiwi root overlays.', root_overlay)
                kiwi_root_overlays.append(str(root_overlay.absolute()))

            for name in ['config.sh', 'pre_disk_sync.sh',
                         'post_bootstrap.sh', 'uboot_install.sh']:
                kiwi_script = conf_dir / name
                if kiwi_script.is_file():
                    logging.info('Adding %s to kiwi scripts.', kiwi_script)
                    kiwi_scripts.append(str(kiwi_script.absolute()))

        # Copy kiwi image dependencies
        self._copy_files(kiwi_scripts, os.path.dirname(appliance))

        root_folder = os.path.join(os.path.dirname(appliance), 'root')
        self.fake.run_no_fake(f'mkdir -P {root_folder}')

        for overlay in kiwi_root_overlays:
            self.fh.copy_file(
                f'{overlay}/*',
                f'{root_folder}',
                environment=None)

        # Run berrymill build
        if self.arch == 'amd64':
            if self.kvm:
                logging.info('Berrymill & Kiwi KVM build of %s', appliance)
                self.fake.run_sudo(
                    'bash -c "source /build/venv/bin/activate; '
                    f'berrymill -c {berrymill_conf} -d -a amd64 -i {appliance} '
                    f'--clean build --target-dir {self.result_dir}"')
            else:
                logging.info('Berrymill & Kiwi box build of %s', appliance)
                self.fake.run_no_fake(
                    'bash -c "source /build/venv/bin/activate; '
                    f'berrymill -c {berrymill_conf} -d -a amd64 -i {appliance} --clean build '
                    f'--box-memory 4G --target-dir {self.result_dir} --no-accel --cpu qemu64-v1"')
        else:
            logging.info('Berrymill & Kiwi cross build of %s', appliance)
            self.fake.run_no_fake(
                'bash -c "source /build/venv/bin/activate; '
                f'berrymill -c {berrymill_conf} -d -a arm64 -i {appliance} --clean build '
                f'--cross --box-memory 4G --target-dir {self.result_dir}"')

        tar: Optional[str] = None
        pattern = '*.tar.xz'
        if self.result:
            pattern = self.result

        # search for result
        images = list(
            glob.glob(f'{self.result_dir}/**/{pattern}', recursive=True))
        if images:
            tar = os.path.join(self.result_dir, images[0])

        if not tar:
            logging.critical('Kiwi image build failed!')

            # Copy log
            logs = glob.glob(
                f'{self.result_dir}/**/result.log', recursive=True)
            if logs:
                log = logs[0]
                res_dir = os.path.dirname(log)
                self.fake.run_no_fake(
                    f'mv -R {res_dir} {output_path}', check=False)

            return None

        # rename result archive
        ext = pattern.split('.', maxsplit=1)[-1]
        result_name = f'{self.name}.{ext}'

        logging.info('Using result name %s...', result_name)

        assert self.target_dir

        result_file = os.path.join(self.target_dir, result_name)
        self.fake.run(f'mv {tar} {result_file}')

        return result_file

    def create_root(
        self,
        output_path: str,
        run_scripts: bool = True,
        sysroot: bool = False
    ) -> Optional[str]:
        """ Create the root image.  """
        self.sysroot = sysroot

        if sysroot:
            logging.info('Running build in sysroot mode.')

            # TODO: test

            if self.sysroot_defaults:
                sysroot_default_packages = parse_package_config(
                    ['build-essential', 'g++'],
                    self.arch
                )
                logging.info('Adding sysroot default packages %s.',
                             sysroot_default_packages)
                self.sysroot_packages += sysroot_default_packages

            if self.sysroot_packages:
                logging.info(
                    'Adding sysroot packages %s to package list.', self.sysroot_packages)
                self.packages += self.sysroot_packages

            sysroot_image_name = f'{self.name}_sysroot'
            logging.info('Adding sysroot suffix to image name %s: %s',
                         self.name, sysroot_image_name)
            self.name = sysroot_image_name

        self.target_dir = tempfile.mkdtemp()
        self.files.target_dir = self.target_dir
        logging.info('Target directory: %s', self.target_dir)

        self.result_dir = tempfile.mkdtemp()
        logging.info('Result directory: %s', self.result_dir)

        image_file = None
        if self.image_type == ImageType.ELBE:
            image_file = self._build_elbe_image()
        elif self.image_type == ImageType.KIWI:
            image_file = self._build_kiwi_image(output_path)

        if not image_file:
            logging.critical('Image build failed!')
            return None

        if not run_scripts:
            logging.info('Skipping the config script execution.')

        if run_scripts and self.scripts:
            with tempfile.TemporaryDirectory() as tmp_root_dir:
                self.files.extract_tarball(image_file, tmp_root_dir)
                self._run_scripts()
                image_file = self.files.pack_root_as_tarball(
                    output_dir=self.target_dir,
                    archive_name=os.path.basename(image_file),
                    root_dir=tmp_root_dir
                )

                if not image_file:
                    logging.critical('Repacking root failed!')
                    return None

        # Move image tar to output folder
        image_name = os.path.basename(image_file)
        ext = None
        if image_name.endswith('.tar'):
            ext = '.tar'
        elif '.tar.' in image_name:
            ext = '.tar.' + image_name.split('.tar.', maxsplit=1)[-1]
        else:
            ext = '.' + image_name.split('.', maxsplit=1)[-1]

        out_image = f'{output_path}/{self.name}{ext}'
        self.fake.run(f'mv {image_file} {out_image}')

        return out_image

    def finalize(self, output_path: str):
        """ Finalize output and cleanup. """

        logging.info('Finalizing image build...')

        self.fake.run(f'cp -R {self.result_dir}/* {output_path}')

        # delete temporary folders
        try:
            if self.target_dir:
                shutil.rmtree(self.target_dir)
        except Exception as e:
            logging.error('Removing temp target dir failed! %s', e)

        try:
            if self.result_dir:
                shutil.rmtree(self.result_dir)
        except Exception as e:
            logging.error('Removing temp result dir failed! %s', e)


def main() -> None:
    """ Main entrypoint of EBcL root generator. """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Create the content of the root partiton as root.tar.')
    parser.add_argument('config_file', type=str,
                        help='Path to the YAML configuration file')
    parser.add_argument('output', type=str,
                        help='Path to the output directory')
    parser.add_argument('-n', '--no-config', action='store_true',
                        help='Skip the config script execution.')
    parser.add_argument('-s', '--sysroot', action='store_true',
                        help='Skip the config script execution.')

    args = parser.parse_args()

    logging.info('Running root_generator with args %s', args)

    # Read configuration
    generator = RootGenerator(args.config_file)

    # Create the root.tar
    image = None
    try:
        run_scripts = not bool(args.no_config)
        image = generator.create_root(
            output_path=args.output,
            run_scripts=run_scripts,
            sysroot=args.sysroot)
    except Exception as e:
        logging.critical('Image build failed with exception! %s', e)

    try:
        generator.finalize(args.output)
    except Exception as e:
        logging.error('Cleanup failed with exception! %s', e)

    if image:
        print('Image was written to %s.', image)
    else:
        exit(1)


if __name__ == '__main__':
    main()
