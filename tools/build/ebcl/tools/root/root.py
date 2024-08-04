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

from ebcl.common import init_logging, bug, promo
from ebcl.common.apt import Apt
from ebcl.common.config import load_yaml
from ebcl.common.fake import Fake
from ebcl.common.files import Files, EnvironmentType, parse_scripts
from ebcl.common.proxy import Proxy
from ebcl.common.templates import render_template
from ebcl.common.version import VersionDepends, parse_package_config


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
    image: Optional[str] = None
    template: Optional[str] = None
    scripts: list[dict[str, Any]]
    apt_repos: list[Apt]
    # build result filename pattern
    result: Optional[str] = None
    # packages to install
    packages: list[VersionDepends]
    # root password
    root_password: str

    use_ebcl_apt: bool

    # sysroot
    sysroot_packages: list[VersionDepends]
    sysroot_defaults: bool
    sysroot: bool

    # kiwi specific parameters
    kvm: bool
    use_berrymill: bool
    berrymill_conf: Optional[str] = None
    use_bootstrap_package: bool
    bootstrap_package: Optional[str]
    bootstrap: Optional[list[VersionDepends]] = None
    use_kiwi_defaults: bool
    kiwi_scripts: list[str]
    kiwi_root_overlays: list[str]
    image_version: str

    # elbe specific parameters
    primary_repo: Optional[Apt] = None
    hostname: str
    domain: str
    console: str
    packer: str

    # Tar the root tarball in the chroot env
    pack_in_chroot: bool

    # fakeroot helper
    fake: Fake
    # proxy
    proxy: Proxy
    # files helper
    fh: Files
    # folder for script execution
    target_dir: Optional[str] = None
    # folder to collect build results
    result_dir: Optional[str] = None

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

        self.pack_in_chroot = config.get('pack_in_chroot', True)

        self.berrymill_conf = config.get('berrymill_conf', None)
        self.use_berrymill = config.get('use_berrymill', True)
        self.use_bootstrap_package = config.get('use_bootstrap_package', True)
        self.bootstrap_package = config.get('bootstrap_package', None)
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

        self.bootstrap = parse_package_config(
            config.get('bootstrap', []), self.arch)

        self.sysroot_packages = parse_package_config(
            config.get('sysroot_packages', []), self.arch)

        self.sysroot_defaults = config.get('sysroot_defaults', True)

        self.proxy = Proxy()
        self.apt_repos = self.proxy.parse_apt_repos(
            apt_repos=config.get('apt_repos', None),
            arch=self.arch,
            ebcl_version=config.get('ebcl_version', None)
        )

        self.use_ebcl_apt = config.get('use_ebcl_apt', False)
        if self.use_ebcl_apt:
            ebcl_apt = Apt.ebcl_apt(self.arch)
            self.proxy.add_apt(ebcl_apt)
            self.apt_repos.append(ebcl_apt)

        if self.primary_repo:
            self.proxy.add_apt(self.primary_repo)

        self.fake = Fake()
        self.fh = Files(self.fake)

    def _run_scripts(self):
        """ Run scripts. """
        for script in self.scripts:
            logging.info('Running script: %s', script)

            file = os.path.join(os.path.dirname(
                self.config), script['name'])

            env: Optional[EnvironmentType] = None
            if 'env' in script:
                env = script['env']

            self.fh.run_script(
                file=file,
                params=script.get('params', None),
                environment=env
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

        if self.arch == 'arm64':
            params['arch'] = 'aarch64'
        else:
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

        if self.packages:
            package_names = []
            for vd in self.packages:
                package_names.append(vd.name)
            params['packages'] = package_names

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

        (image_file, _content) = render_template(
            template_file=template,
            params=params,
            generated_file_name=f'{self.name}.image.xml',
            results_folder=self.result_dir,
            template_copy_folder=self.result_dir
        )

        if not image_file:
            logging.critical('Rendering image description failed!')
            return None

        logging.debug('Generated image stored as %s', image_file)

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
            f'elbe preprocess --output={pre_xml} {image.absolute()}')
        self.fake.run_no_fake(
            f'elbe control set_xml {prj} {pre_xml}')
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

        return ''

    def _generate_kiwi_image(self, generate_repos: bool = False) -> Optional[str]:
        """ Generate a kiwi image description. """
        assert self.result_dir

        # TODO: test

        if not self.apt_repos:
            logging.critical('No apt repositories defined!')
            return None

        bootstrap_package = None
        if self.use_bootstrap_package:
            bootstrap_package = self.bootstrap_package
            if not bootstrap_package:
                bootstrap_package = 'bootstrap-root-ubuntu-jammy'
                logging.info('No bootstrap paackage provided. '
                             'Using default package %s.', bootstrap_package)

        params: dict[str, Any] = {}

        if generate_repos:
            kiwi_repos = self._generate_kiwi_repo_config()
            if kiwi_repos:
                params['repos'] = kiwi_repos

        if self.arch == 'arm64':
            params['arch'] = 'aarch64'
        else:
            params['arch'] = 'x86_64'

        params['version'] = self.image_version
        params['root_password'] = self.root_password

        if self.packages:
            package_names = []
            for vd in self.packages:
                package_names.append(vd.name)
            params['packages'] = package_names

        if bootstrap_package:
            params['bootstrap_package'] = bootstrap_package

        if self.bootstrap:
            package_names = []
            for vd in self.bootstrap:
                package_names.append(vd.name)
            params['bootstrap'] = package_names

        if self.template is None:
            template = os.path.join(os.path.dirname(__file__), 'root.kiwi')
        else:
            template = os.path.join(
                os.path.dirname(self.config), self.template)

        (image_file, _content) = render_template(
            template_file=template,
            params=params,
            generated_file_name=f'{self.name}.image.kiwi',
            results_folder=self.result_dir,
            template_copy_folder=self.result_dir
        )

        if not image_file:
            logging.critical('Rendering image description failed!')
            return None

        logging.debug('Generated image stored as %s', image_file)

        return image_file

    def _generate_kiwi_repo_config(self) -> Optional[str]:
        """ Generate repos as kiwi XML tags. """

        # TODO: test

        repos = ''

        cnt = 0
        for apt in self.apt_repos:

            if apt.key_url or apt.key_gpg:
                logging.warning(
                    'Apt repository key checks are not supported for kiwi-only build!')

            for component in apt.components:
                cmp_id = f'{cnt}_{apt.distro}_{component}'
                repos += f'<repository alias=”{cmp_id}" type="apt-deb" ' \
                    f'distribution="{apt.distro}" components="{component}" ' \
                    f'use_for_bootstrap="{cnt == 0}" repository_gpgcheck="false" >\n'
                repos += f'    <source path = "{apt.url}" />\n'
                repos += '</repository>\n\n'

            cnt += 1

        return repos

    def _generate_berrymill_config(self) -> Optional[str]:
        """ Generate a berrymill.conf. """
        assert self.result_dir

        # TODO: test

        berrymill_conf: dict[str, Any] = {}

        berrymill_conf['use-global-repos'] = False
        berrymill_conf['boxed_plugin_conf'] = '/etc/berrymill/kiwi_boxed_plugin.yml'
        berrymill_conf['repos'] = {}
        berrymill_conf['repos']['release'] = {}

        cnt = 1
        for apt in self.apt_repos:
            apt_repo_key = None
            (_pub, apt_repo_key) = apt.get_key_files(self.result_dir)
            if not apt_repo_key:
                logging.error('No key found for %s, skipping repo!', apt)
                continue

            if apt.arch not in berrymill_conf['repos']['release']:
                berrymill_conf['repos']['release'][apt.arch] = {}

            for component in apt.components:
                cmp_id = f'{cnt}_{apt.distro}_{component}'
                cnt += 1

                berrymill_conf['repos']['release'][apt.arch][cmp_id] = {
                    'url': apt.url,
                    'type': 'apt-deb',
                    'key': f'file://{apt_repo_key}',
                    'name': apt.distro,
                    'components': component
                }

        config_file = os.path.join(self.result_dir, 'berrymill.conf')

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                data = yaml.dump(berrymill_conf)
                logging.debug('Berrymill configuration: %s', data)
                f.write(data)
        except Exception as e:
            logging.critical('Saving berrymill.conf failed! %s', e)
            return None

        logging.debug('Berrymill configuration written to %s.', config_file)

        return config_file

    def _copy_files(self, files: list[str], dst: str):
        """ Copy files to dst. """
        logging.debug('Files: %s', files)

        for file in files:
            src = os.path.join(os.path.dirname(self.config), file)

            logging.info('Copying file %s...', file)

            self.fh.copy_file(
                src=str(src),
                dst=str(dst),
            )

    def _build_kiwi_image(self) -> Optional[str]:
        """ Run kiwi image build. """
        assert self.result_dir

        berrymill_conf = None
        use_berrymill = self.use_berrymill

        if use_berrymill:
            berrymill_conf = self.berrymill_conf
            if berrymill_conf:
                berrymill_conf = os.path.abspath(os.path.join(
                    os.path.dirname(self.config), berrymill_conf))
            else:
                logging.info('Generating the berrymill.conf...')
                berrymill_conf = self._generate_berrymill_config()
                if not berrymill_conf:
                    logging.critical('Generating a berrymill.conf failed!')
                    return None

        if not berrymill_conf:
            logging.warning(
                'No berrymill.conf, falling back to kiwi-only build.')
            use_berrymill = False

        if not self.image:
            generate_repos = not use_berrymill
            self.image = self._generate_kiwi_image(generate_repos)

        if not self.image:
            logging.critical('No kiwi image description found!')
            return None

        image = Path(os.path.join(os.path.dirname(self.config), self.image))
        if not image.is_file():
            logging.critical('Image %s not found!', image)
            return None

        logging.debug('Berrymill.conf: %s', berrymill_conf)

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
        self.fake.run_no_fake(f'mkdir -p {root_folder}')

        for overlay in kiwi_root_overlays:
            self.fh.copy_file(
                f'{overlay}/*',
                f'{root_folder}',
                environment=None)

        # Ensure kiwi boxes are accessible
        self.fake.run_sudo('chmod -R 777 /home/ebcl/.kiwi_boxes', check=False)

        accel = ''
        if not self.kvm:
            accel = '--no-accel'

        cmd = None
        if use_berrymill:
            logging.info(
                'Berrymill & Kiwi KVM build of %s (KVM: %s).', appliance, self.kvm)
            cmd = f'berrymill -c {berrymill_conf} -d -a {self.arch} -i {appliance} ' \
                f'--clean build --box-memory 4G  --cpu qemu64-v1 {accel} ' \
                f'--target-dir {self.result_dir}'
        else:
            logging.info('Kiwi KVM build of %s (KVM: %s).',
                         appliance, self.kvm)

            box_arch = '--x86_64'
            if self.arch == 'arm64':
                box_arch = '--aarch64'

            cmd = f'kiwi-ng --debug --target-arch={self.arch} ' \
                f'--kiwi-file={os.path.basename(appliance)} ' \
                f'system boxbuild {box_arch} ' \
                f'--box ubuntu --box-memory=4G --cpu=qemu64-v1 {accel} -- ' \
                f'--description={os.path.dirname(appliance)} ' \
                f'--target-dir={self.result_dir}'

        fn_run = self.fake.run_sudo
        if not self.kvm:
            fn_run = self.fake.run_no_fake
            cmd = f'bash -c "{cmd}"'

        fn_run(f'. /build/venv/bin/activate && {cmd}')

        if self.kvm:
            # Fix ownership - needed for KVM build which is executed as root
            self.fake.run_sudo(
                f'chown -R ebcl:ebcl {self.result_dir}', check=False)

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
            logging.debug('Apt repos: %s', self.apt_repos)
            return None

        # rename result archive
        ext = pattern.split('.', maxsplit=1)[-1]
        result_name = f'{self.name}.{ext}'

        logging.debug('Using result name %s...', result_name)

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
        self.fh.target_dir = self.target_dir
        logging.debug('Target directory: %s', self.target_dir)

        self.result_dir = tempfile.mkdtemp()
        logging.debug('Result directory: %s', self.result_dir)

        image_file = None
        if self.image_type == ImageType.ELBE:
            image_file = self._build_elbe_image()
        elif self.image_type == ImageType.KIWI:
            image_file = self._build_kiwi_image()

        if not image_file:
            logging.critical('Image build failed!')
            return None

        if not run_scripts:
            logging.info('Skipping the config script execution.')

        if run_scripts and self.scripts:
            with tempfile.TemporaryDirectory() as tmp_root_dir:
                self.fh.extract_tarball(image_file, tmp_root_dir)
                self._run_scripts()
                image_file = self.fh.pack_root_as_tarball(
                    output_dir=self.target_dir,
                    archive_name=os.path.basename(image_file),
                    root_dir=tmp_root_dir,
                    use_fake_chroot=self.pack_in_chroot
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

        # Fix ownership
        try:
            self.fake.run_sudo(
                f'chown -R ebcl:ebcl {self.result_dir}')
        except Exception as e:
            logging.error('Fixing ownership failed! %s', e)

        try:
            self.fake.run(f'cp -R {self.result_dir}/* {output_path}')
        except Exception as e:
            logging.error('Copying all artefacts failed! %s', e)

        if logging.root.level == logging.DEBUG:
            logging.info(
                'Log level set to debug, skipping cleanup of build artefacts.')
            logging.info('Target folder: %s', self.target_dir)
            logging.info('Results folder: %s', self.result_dir)
            return

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
    init_logging('DEBUG')

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

    logging.debug('Running root_generator with args %s', args)

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
        bug()

    try:
        generator.finalize(args.output)
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
