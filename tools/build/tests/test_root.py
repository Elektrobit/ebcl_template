""" Unit tests for the EBcL boot generator. """
import os
import shutil
import tempfile

from pathlib import Path

from ebcl.root import RootGenerator, ImageType


class TestRoot:
    """ Unit tests for the EBcL boot generator. """

    yaml: str
    target_dir: str
    result_dir: str
    generator: RootGenerator

    @classmethod
    def setup_class(cls):
        """ Prepare initrd generator. """
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.yaml = os.path.join(test_dir, 'data', 'root.yaml')
        # Prepare generator
        cls.generator = RootGenerator(cls.yaml)

        cls.result_dir = tempfile.mkdtemp()
        cls.generator.result_dir = cls.result_dir

        cls.target_dir = tempfile.mkdtemp()
        cls.generator.target_dir = cls.target_dir

    @classmethod
    def teardown_class(cls):
        """ Remove temp_dir. """
        shutil.rmtree(cls.target_dir)
        shutil.rmtree(cls.result_dir)

    def test_read_config(self):
        """ Test yaml config loading. """
        assert self.generator.image == 'ubuntu:22.04'
        assert self.generator.image_type == ImageType.ELBE

    def test_build_kiwi_image(self):
        """ Test kiwi image build. """
        test_dir = os.path.dirname(os.path.abspath(__file__))
        yaml = os.path.join(test_dir, 'data', 'root_kiwi.yaml')
        generator = RootGenerator(yaml)
        generator.result_dir = tempfile.mkdtemp()
        generator.target_dir = tempfile.mkdtemp()

        archive = generator._build_kiwi_image()
        assert archive
        assert os.path.isfile(archive)

        shutil.rmtree(generator.result_dir)
        shutil.rmtree(generator.target_dir)

    def test_build_root_archive(self):
        """ Test build root.tar. """
        out = tempfile.mkdtemp()
        self.generator.create_root(out)

        archive = Path(out) / 'ubuntu.tar'
        assert archive.is_file()
