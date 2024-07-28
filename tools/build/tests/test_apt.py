""" Tests for the apt functions. """
import os
import tempfile

from pathlib import Path

from ebcl.apt import Apt, download_deb_packages
from ebcl.cache import Cache


class TestApt:
    """ Tests for the apt functions. """

    apt: Apt

    @classmethod
    def setup_class(cls):
        """ Prepare apt repo object. """
        cls.apt = Apt()

    def test_find_busybox_default(self):
        """ Search busybox package in default apt repository. """
        p = self.apt.find_package('busybox-static')
        assert p is not None
        assert p.name == 'busybox-static'
        assert p.file_url is not None

    def test_download_busybox(self):
        """ Search busybox package in default apt repository. """
        p = self.apt.find_package('busybox-static')
        assert p is not None

        with tempfile.TemporaryDirectory() as d:
            file = p.download(d)
            assert file is not None
            assert os.path.isfile(file)

    def test_ebcl_apt(self):
        """ Test that EBcL apt repo works and provides busybox-static. """
        apt = Apt(
            url='https://linux.elektrobit.com/eb-corbos-linux/1.2',
            distro='ebcl',
            components=['prod', 'dev'],
            arch='arm64'
        )

        p = apt.find_package('busybox-static')
        assert p is not None
        assert p.name == 'busybox-static'
        assert p.file_url is not None

    def test_find_linux_image_generic(self):
        """ Search busybox package in default apt repository. """
        p = self.apt.find_package('linux-image-generic')
        assert p is not None
        assert p.name == 'linux-image-generic'
        assert p.file_url is not None
        assert p.depends is not None

        deps = p.get_depends()
        assert deps is not []

    def test_download_and_extract_linux_image(self):
        """ Extract data content of multiple debs. """

        (debs, content, missing) = download_deb_packages(
            'amd64',
            [self.apt],
            ['linux-image-generic'],
            cache=Cache())

        assert not missing

        deb_path = Path(debs)
        packages = list(deb_path.glob('*.deb'))

        assert len(packages) > 0

        content_path = Path(content)
        boot = content_path / 'boot'
        kernel_images = list(boot.glob('vmlinuz*'))

        assert len(kernel_images) > 0
