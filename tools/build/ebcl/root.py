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

from jinja2 import Template

from .apt import Apt
from .config import load_yaml
from .fake import Fake
from .files import Files, EnvironmentType


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
    apt_repos: list[Apt] = []
    name: str
    arch: str
    image_type: ImageType
    image: Optional[str]
    template: Optional[str]
    scripts: list[dict[str, str]]
    # build result filename pattern
    result: Optional[str]

    # packages to install
    packages: list[str]

    # kiwi specific parameters
    kvm: bool
    berrymill_conf: Optional[str]

    # elbe specific parameters
    primary_repo: Optional[Apt]
    hostname: str
    domain: str
    root_password: str
    console: str
    packer: str

    # fakeroot helper
    fake: Fake
    # files helper
    files: Files
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
        self.kvm = config.get('kvm', True)

        self.scripts = config.get('scripts', [])

        self.image = config.get('image', None)
        self.template = config.get('template', None)

        self. berrymill_conf = config.get(
            'berrymill_conf', None)

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

        self.hostname = config.get('hostname', 'ebcl')
        self.domain = config.get('domain', 'elektrobit.com')
        self.root_password = config.get('root_password', 'linux')
        self.console = config.get('console', 'ttyAMA0,115200')
        self.packer = config.get('packer', 'none')

        self.packages = config.get('packages', [])

        repos: Optional[list[dict[str, Any]]] = config.get('apt_repos', None)
        if repos:
            self.apt_repos = []
            for repo in repos:
                self.apt_repos.append(
                    Apt(
                        url=repo['apt_repo'],
                        distro=repo['distro'],
                        components=repo['components'],
                        arch=self.arch
                    )
                )

        if self.primary_repo:
            self.apt_repos.append(self.primary_repo)

        self.fake = Fake()
        self.files = Files(self.fake)

    def _run_scripts(self):
        """ Run scripts. """
        for script in self.scripts:
            script_path = script['name']

            params = ''
            if 'params' in script:
                params = script['params']

            env = EnvironmentType.FAKEROOT
            if 'env' in script:
                e = EnvironmentType.from_str(script['env'])
                if e:
                    env = e
                else:
                    logging.error(
                        'Unknown environment %s for script %s!', script['env'], script['name'])

            script_file = os.path.abspath(os.path.join(
                os.path.dirname(self.config), script_path))

            logging.info('Running script %s in env %s', script, env)

            if not os.path.isfile(script_file):
                logging.error('Script %s not found!', script)
                continue

            res = self.files.run_script(script_file, params, env)
            if not res:
                logging.error('Execution of script %s failed!', script_file)
            else:
                (_out, _err, returncode) = res
                if returncode != 0:
                    logging.error(
                        'Execution of script %s failed with return code %s!',
                        script_file, returncode)

    def _generate_elbe_image(self) -> Optional[str]:
        assert self.result_dir

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

    def _build_kiwi_image(self, output_path: str) -> Optional[str]:
        """ Run kiwi image build. """
        assert self.result_dir

        # TODO: template

        if not self.image:
            logging.critical('No kiwi image description found!')
            return None

        image = Path(os.path.join(os.path.dirname(self.config), self.image))
        if not image.is_file():
            logging.critical('Image %s not found!', image)
            return None

        berrymill_conf = '/etc/berrymill/berrymill.conf'
        if self.berrymill_conf:
            berrymill_conf = self.berrymill_conf

        logging.info('Berrymill.conf: %s', berrymill_conf)

        appliance = os.path.join(self.result_dir, image.name)
        shutil.copy(image, appliance)

        scripts = glob.glob(f'{image.parent.absolute()}/*.sh', recursive=True)
        for script in scripts:
            shutil.copy(script, os.path.dirname(appliance))

        overlay = os.path.join(os.path.dirname(image), 'root')
        if os.path.isdir(overlay):
            shutil.copytree(overlay, os.path.dirname(appliance))

        if self.arch == 'amd64':
            if self.kvm:
                logging.info('Kiwi KVM build of %s', appliance)
                self.fake.run_sudo(
                    'bash -c "source /build/venv/bin/activate; '
                    f'berrymill -c {berrymill_conf} -d -a amd64 -i {appliance} '
                    f'--clean build --target-dir {self.result_dir}"')
            else:
                logging.info('Kiwi box build of %s', appliance)
                self.fake.run_no_fake(
                    'bash -c "source /build/venv/bin/activate; '
                    f'berrymill -c {berrymill_conf} -d -a amd64 -i {appliance} --clean build '
                    f'--box-memory 4G --target-dir {self.result_dir} --no-accel --cpu qemu64-v1"')
        else:
            logging.info('Kiwi cross build of %s', appliance)
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

            exit(1)

        # rename result archive
        ext = pattern.split('.', maxsplit=1)[-1]
        result_name = f'{self.name}.{ext}'

        logging.info('Using result name %s...', result_name)

        assert self.target_dir

        result_file = os.path.join(self.target_dir, result_name)
        self.fake.run(f'mv {tar} {result_file}')

        return result_file

    def create_root(self, output_path: str, run_scripts: bool = True) -> Optional[str]:
        """ Create the root image.  """
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
        description='Create the content of the boot partiton as boot.tar.')
    parser.add_argument('config_file', type=str,
                        help='Path to the YAML configuration file')
    parser.add_argument('output', type=str,
                        help='Path to the output directory')
    parser.add_argument('-nc', '--no-config', action='store_true',
                        help='Skip the config script execution.')

    args = parser.parse_args()

    logging.info('Running root_generator with args %s', args)

    # Read configuration
    generator = RootGenerator(args.config_file)

    # Create the boot.tar
    image = None
    try:
        run_scripts = not bool(args.no_config)
        image = generator.create_root(
            output_path=args.output,
            run_scripts=run_scripts)
    except Exception as e:
        logging.critical('Image build failed with exception! %s', e)

    generator.finalize(args.output)
    if image:
        print('Image was written to %s.', image)
    else:
        exit(1)


if __name__ == '__main__':
    main()
