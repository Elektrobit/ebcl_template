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
from typing import Optional

from .config import load_yaml
from ebcl.fake import Fake


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


class ScriptType(Enum):
    """ Enum for supported script types. """
    CONFIG = 1
    PRE_DISC = 2
    POST_DISC = 3

    @classmethod
    def from_str(cls, script_type: str):
        """ Get ImageType from str. """
        if script_type == 'config':
            return cls.CONFIG
        elif script_type == 'pre_disc':
            return cls.PRE_DISC
        elif script_type == 'post_disc':
            return cls.POST_DISC
        else:
            return None

    def __str__(self) -> str:
        if self.value == 1:
            return "config"
        elif self.value == 2:
            return "pre_disc"
        elif self.value == 3:
            return "post_disc"
        else:
            return "UNKNOWN"


class RootGenerator:
    """ EBcL root filesystem generator. """
    # config file
    config: str
    # config values
    name: str
    image_type: ImageType
    image: str
    scripts: list[dict[str, str]]
    arch: str
    result: str
    kvm: bool
    berrymill_conf: Optional[str]
    # fakeroot helper
    fake: Fake
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
        self.result = config.get('result', '*.tar')
        self.scripts = config.get('scripts', [])
        self. berrymill_conf = config.get(
            'berrymill_conf', None)

        self.image = config.get('image', '')
        if not self.image:
            logging.critical('Missing mandatory config value \'image\'!')
            exit(1)

        self.name = config.get('name', '')
        if not self.name:
            self.name = os.path.basename(self.image)

        self.image_type = ImageType.from_str(config.get('type', 'docker'))
        logging.info('Using image type: %s', self.image_type)

        self.fake = Fake()

    def _run_scripts(self):
        """ Run scripts. """
        assert self.target_dir

        for script in self.scripts:
            script_path = script['name']
            script_file = os.path.abspath(os.path.join(
                os.path.dirname(self.config), script_path))

            script_type = ScriptType.from_str(script.get('type', 'config'))

            logging.info('Running %s script: %s', script_type, script)

            if not os.path.isfile(script_file):
                logging.error('Script %s not found!', script)
                continue

            if script_type == ScriptType.CONFIG or script_type == ScriptType.PRE_DISC:
                script_name = os.path.basename(script_file)
                target_file = os.path.abspath(
                    os.path.join(self.target_dir, script_name))
                self.fake.run(f'cp {script_file} {target_file}')
                self.fake.run_chroot(f'/{script_name}', self.target_dir)
                self.fake.run(f'rm {target_file}')
            elif script_type == ScriptType.POST_DISC:
                self.fake.run(f'{script_file} {self.target_dir}',
                              cwd=self.target_dir)
            else:
                logging.error(
                    'Skipping script %s with unknown type %s.', script_file, script_type)

    def _extract_image(self, archive: str):
        """ Extract tar archive to target_dir. """
        assert self.target_dir

        tar_file = Path(archive)
        assert tar_file.is_file() or tar_file.is_symlink()

        if tar_file.parent.absolute() != self.target_dir:
            dst = Path(self.target_dir) / tar_file.name
            self.fake.run(f'cp {tar_file.absolute()} {dst.absolute()}')
            tar_file = dst

        self.fake.run(f'tar xf {tar_file.name}', cwd=self.target_dir)

    def _pack_image(self) -> str:
        """ Create tar archive of target_dir. """
        assert self.target_dir
        assert self.result_dir

        archive = os.path.join(self.target_dir, f'{self.name}.tar')
        if os.path.isfile(archive):
            logging.info('Archive %s exists. Deleting old archive.', archive)
            os.remove(archive)

        self.fake.run(
            f'tar -cvf {os.path.basename(archive)} .', cwd=self.target_dir)

        dst = os.path.join(self.result_dir, os.path.basename(archive))

        if os.path.isfile(dst):
            os.remove(dst)

        self.fake.run(f'mv {archive} {dst}')

        return dst

    def _build_elbe_image(self) -> Optional[str]:
        """ Run elbe image build. """
        assert self.result_dir

        image = Path(os.path.join(os.path.dirname(self.config), self.image))
        if not image.is_file():
            logging.critical('Image %s not found!', image)
            return None

        (out, err) = self.fake.run_no_fake('elbe control create_project')
        assert not err
        assert out
        prj = out.strip()

        pre_xml = os.path.join(self.result_dir, image.name) + '.gz'
        self.fake.run_no_fake(
            f'elbe preprocess --output={pre_xml} {image.absolute()}')
        self.fake.run_no_fake(f'elbe control set_xml {prj} {pre_xml}')
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
        images = list(results.glob(self.result))
        if images:
            return os.path.join(self.result_dir, images[0])

        return None

    def _build_kiwi_image(self) -> Optional[str]:
        """ Run kiwi image build. """
        assert self.result_dir

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
                self.fake.run_sudo(
                    'bash -c "source /build/venv/bin/activate; '
                    f'berrymill -c {berrymill_conf} -d -a amd64 -i {appliance} '
                    f'--clean build --target-dir {self.result_dir}"')
            else:
                self.fake.run_no_fake(
                    'bash -c "source /build/venv/bin/activate; '
                    f'berrymill -c {berrymill_conf} -d -a amd64 -i {appliance} --clean build '
                    f'--box-memory 4G --target-dir {self.result_dir} --no-accel --cpu qemu64-v1"')
        else:
            self.fake.run_no_fake(
                'bash -c "source /build/venv/bin/activate; '
                f'berrymill -c {berrymill_conf} -d -a arm64 -i {appliance} --clean build '
                f'--cross --box-memory 4G --target-dir {self.result_dir}"')

        # search for tar.xz
        images = list(
            glob.glob(f'{self.result_dir}/**/*.tar.xz', recursive=True))
        if images:
            return os.path.join(self.result_dir, images[0])

        # search for image
        images = list(
            glob.glob(f'{self.result_dir}/**/{self.result}', recursive=True))
        if images:
            return os.path.join(self.result_dir, images[0])

        return None

    def create_root(self, output_path: str) -> None:
        """ Create the root image.  """
        self.target_dir = tempfile.mkdtemp()
        logging.info('Target directory: %s', self.target_dir)
        self.result_dir = tempfile.mkdtemp()
        logging.info('Result directory: %s', self.result_dir)

        image_file = None
        if self.image_type == ImageType.ELBE:
            image_file = self._build_elbe_image()
        elif self.image_type == ImageType.KIWI:
            image_file = self._build_kiwi_image()

        if image_file is None:
            logging.critical('Image build failed!')
            return

        assert image_file

        if self.scripts:
            self._extract_image(image_file)
            self._run_scripts()
            image_file = self._pack_image()

        # Move image tar to output folder
        ext = os.path.basename(image_file).split('.', maxsplit=1)[-1]
        out_image = f'{output_path}/{self.name}.{ext}'
        self.fake.run(f'mv {image_file} {out_image}')

        self.fake.run(f'cp -R {self.result_dir}/* {output_path}')

        # delete temporary folders
        shutil.rmtree(self.target_dir)
        shutil.rmtree(self.result_dir)


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
    generator = RootGenerator(args.config_file)

    # Create the boot.tar
    generator.create_root(args.output)


if __name__ == '__main__':
    main()
