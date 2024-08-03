""" Unit tests for the EBcL initrd generator. """
import os
import shutil
import tempfile

from pathlib import Path

from ebcl.common.fake import Fake
from ebcl.tools.initrd.initrd import InitrdGenerator
from ebcl.common.version import VersionDepends


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
        fake = Fake()
        fake.run_sudo(f'rm -rf {cls.temp_dir}')

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
        vd = VersionDepends(
            name='linux-modules-5.15.0-1023-s32-eb',
            package_relation=None,
            version_relation=None,
            version=None,
            arch=self.generator.arch
        )
        package = self.generator.proxy.find_package(vd)
        assert package

        pkg = self.generator.proxy.download_package(
            self.generator.arch, package)
        assert pkg
        assert pkg.local_file
        assert os.path.isfile(pkg.local_file)

    def test_extract_modules_from_deb(self):
        """ Test modules package download. """
        vd = VersionDepends(
            name='linux-modules-5.15.0-1023-s32-eb',
            package_relation=None,
            version_relation=None,
            version=None,
            arch=self.generator.arch
        )
        package = self.generator.proxy.find_package(vd)
        assert package

        pkg = self.generator.proxy.download_package(
            self.generator.arch, package)
        assert pkg
        assert pkg.local_file
        assert os.path.isfile(pkg.local_file)

        mods_temp = tempfile.mkdtemp()

        pkg.extract(mods_temp)

        module = 'kernel/pfeng/pfeng.ko'
        self.generator.modules = [module]

        kversion = self.generator.find_kernel_version(mods_temp)

        self.generator.extract_modules_from_deb(mods_temp)

        shutil.rmtree(mods_temp)

        assert os.path.isfile(os.path.join(
            self.temp_dir, 'lib', 'modules', kversion, module))

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

        (out, err, _returncode) = fake.run_sudo(
            f'stat -c \'%a\' {self.temp_dir}/root/dummy.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '666'
        assert not err.strip()

        (out, err, _returncode) = fake.run_sudo(
            f'stat -c \'%u %g\' {self.temp_dir}/root/dummy.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '0 0'
        assert not err.strip()

        (out, err, _returncode) = fake.run_sudo(
            f'stat -c \'%a\' {self.temp_dir}/root/other.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '700'

        (out, err, _returncode) = fake.run_sudo(
            f'stat -c \'%u %g\' {self.temp_dir}/root/other.txt')
        assert out is not None
        out = out.split('\n')[-2]
        assert out.strip() == '123 456'
        assert not err.strip()

    def test_sysroot_is_created(self):
        """ Test that sysroot folder is created. """
        temp_dir = tempfile.mkdtemp()

        self.generator.create_initrd(temp_dir)

        out = os.path.join(temp_dir, 'initrd.img')
        assert os.path.isfile(out)

        shutil.rmtree(temp_dir)
