""" Unit tests for the EBcL boot generator. """
import os
import shutil
import tempfile

from pathlib import Path

from ebcl.tools.boot.boot import BootGenerator


class TestBoot:
    """ Unit tests for the EBcL boot generator. """

    yaml: str
    temp_dir: str
    generator: BootGenerator

    @classmethod
    def setup_class(cls):
        """ Prepare initrd generator. """
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.yaml = os.path.join(test_dir, 'data', 'boot.yaml')
        # Prepare generator
        cls.generator = BootGenerator(cls.yaml)
        cls.temp_dir = tempfile.mkdtemp()
        cls.generator.target_dir = cls.temp_dir

    @classmethod
    def teardown_class(cls):
        """ Remove temp_dir. """
        shutil.rmtree(cls.temp_dir)

    def test_read_config(self):
        """ Test yaml config loading. """
        generator = BootGenerator(self.yaml)
        assert generator.arch == 'amd64'

    def test_build_boot_archive(self):
        """ Test build boot.tar. """
        self.generator.create_boot(self.temp_dir)

        archive = Path(self.temp_dir) / 'boot.tar'
        assert archive.is_file()
