""" Unit tests for the EBcL boot generator. """
import os
import shutil
import tempfile

from ebcl.common.apt import Apt
from ebcl.tools.root.root import RootGenerator, ImageType


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
        assert self.generator.image is None
        assert self.generator.image_type == ImageType.ELBE

    def test_build_kiwi_image(self):
        """ Test kiwi image build. """
        out = tempfile.mkdtemp()

        test_dir = os.path.dirname(os.path.abspath(__file__))
        yaml = os.path.join(test_dir, 'data', 'root_kiwi.yaml')
        generator = RootGenerator(yaml)

        generator.apt_repos = [Apt.ebcl_apt('amd64')]

        archive = generator.create_root(out)
        assert archive
        assert os.path.isfile(archive)

        shutil.rmtree(out)

    def test_build_root_archive(self):
        """ Test build root.tar. """
        out = tempfile.mkdtemp()

        test_dir = os.path.dirname(os.path.abspath(__file__))
        yaml = os.path.join(test_dir, 'data', 'root_elbe.yaml')
        generator = RootGenerator(yaml)

        generator.apt_repos = [Apt.ebcl_apt('amd64')]

        archive = generator.create_root(out)
        assert archive
        assert os.path.isfile(archive)

        shutil.rmtree(out)

    def test_build_kiwi_no_berry(self):
        """ Test kiwi image build without berrymill. """
        out = tempfile.mkdtemp()

        test_dir = os.path.dirname(os.path.abspath(__file__))
        yaml = os.path.join(test_dir, 'data', 'root_kiwi_berry.yaml')
        generator = RootGenerator(yaml)

        generator.apt_repos = [Apt.ebcl_apt('amd64')]

        archive = generator.create_root(out)
        assert archive
        assert os.path.isfile(archive)

        shutil.rmtree(out)

    def test_build_kiwi_no_bootstrap(self):
        """ Test kiwi image build without bootstrap package. """
        out = tempfile.mkdtemp()

        test_dir = os.path.dirname(os.path.abspath(__file__))
        yaml = os.path.join(test_dir, 'data', 'root_kiwi_debo.yaml')
        generator = RootGenerator(yaml)

        generator.apt_repos = [Apt()]

        archive = generator.create_root(out)
        assert archive
        assert os.path.isfile(archive)

        # shutil.rmtree(out)

    def test_build_sysroot_kiwi(self):
        """ Test kiwi image build. """
        out = tempfile.mkdtemp()

        test_dir = os.path.dirname(os.path.abspath(__file__))
        yaml = os.path.join(test_dir, 'data', 'sysroot_kiwi.yaml')
        generator = RootGenerator(yaml)

        generator.apt_repos = [Apt.ebcl_apt('amd64')]

        archive = generator.create_root(out)
        assert archive
        assert os.path.isfile(archive)

        shutil.rmtree(out)

    def test_build_sysroot_elbe(self):
        """ Test build root.tar. """
        out = tempfile.mkdtemp()

        test_dir = os.path.dirname(os.path.abspath(__file__))
        yaml = os.path.join(test_dir, 'data', 'sysroot_elbe.yaml')
        generator = RootGenerator(yaml)

        generator.apt_repos = [Apt.ebcl_apt('amd64')]

        archive = generator.create_root(out)
        assert archive
        assert os.path.isfile(archive)

        shutil.rmtree(out)
