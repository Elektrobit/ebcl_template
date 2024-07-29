""" Unit tests for the EBcL initrd generator. """
import os
import shutil
import tempfile

from pathlib import Path

from ebcl.fake import Fake
from ebcl.initrd import InitrdGenerator
from ebcl.proxy import Proxy


class TestInitrd:
    """ Unit tests for the EBcL initrd generator. """

    yaml: str
    temp_dir: str
    generator: InitrdGenerator

    @classmethod
    def setup_class(cls):
        """ Prepare initrd generator. """
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.yaml = os.path.join(test_dir, 'data', 'initrd.yaml')
        # Prepare generator
        cls.generator = InitrdGenerator(cls.yaml)
        cls.temp_dir = tempfile.mkdtemp()
        cls.generator.target_dir = cls.temp_dir

    @classmethod
    def teardown_class(cls):
        """ Remove temp_dir. """
        shutil.rmtree(cls.temp_dir)

    def test_read_config(self):
        """ Test yaml config loading. """
        generator = InitrdGenerator(self.yaml)
        assert generator.arch == 'arm64'
        assert generator.root_device == '/dev/mmcblk0p2'

    def test_install_busybox(self):
        """ Test yaml config loading. """
        self.generator.install_busybox()

        assert os.path.isfile(os.path.join(
            self.generator.target_dir, 'bin', 'busybox'))
        assert os.path.islink(os.path.join(
            self.generator.target_dir, 'bin', 'sh'))

    def test_download_deb_package(self):
        """ Test modules package download. """
        package = self.generator.proxy.find_package(
            self.generator.arch,
            'linux-modules-5.15.0-1023-s32-eb')
        assert package is not None

        local_deb = package.download()
        assert local_deb is not None
        assert os.path.isfile(local_deb)

    def test_extract_modules_from_deb(self):
        """ Test modules package download. """
        package = self.generator.proxy.find_package(
            self.generator.arch,
            'linux-modules-5.15.0-1023-s32-eb')
        assert package
        package.download()
        mods_temp = tempfile.mkdtemp()
        package.extract(mods_temp)

        module = 'kernel/pfeng/pfeng.ko'
        self.generator.modules = [module]

        self.generator.extract_modules_from_deb(mods_temp)

        shutil.rmtree(mods_temp)

        assert os.path.isfile(os.path.join(
            self.temp_dir, 'lib', 'modules', self.generator.kversion, module))

    def test_add_devices(self):
        """ Test device node creation. """
        self.generator.devices = [{
            'name': 'console',
            'type': 'char',
            'major': '5',
            'minor': '1',
        }]

        self.generator.install_busybox()
        self.generator.add_devices()

        device = Path(self.temp_dir) / 'dev' / 'console'
        assert device.is_char_device()

    def test_copy_files(self):
        """ Test copying of files. """
        self.generator.files = [
            {
                'source': 'dummy.txt',
                'destination': 'root'
            },
            {
                'source': 'other.txt',
                'destination': 'root',
                'mode': '700',
                'uid': '123',
                'gid': '456'
            }
        ]

        os.mkdir(os.path.join(self.temp_dir, 'root'))

        self.generator.install_busybox()
        self.generator.copy_files()

        fake = Fake()

        (out, err) = fake.run_sudo(
            f'stat -c \'%a\' {self.temp_dir}/root/dummy.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '666'
        assert not err.strip()

        (out, err) = fake.run_sudo(
            f'stat -c \'%u %g\' {self.temp_dir}/root/dummy.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '0 0'
        assert not err.strip()

        (out, err) = fake.run_sudo(
            f'stat -c \'%a\' {self.temp_dir}/root/other.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '700'

        (out, err) = fake.run_sudo(
            f'stat -c \'%u %g\' {self.temp_dir}/root/other.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '123 456'
        assert not err.strip()

    def test_sysroot_is_created(self):
        """ Test that sysroot folder is created. """
        temp_dir = tempfile.mkdtemp()
        out = os.path.join(temp_dir, 'initrd.img')
        self.generator.create_initrd(out)

        assert os.path.isfile(out)

        shutil.rmtree(temp_dir)
