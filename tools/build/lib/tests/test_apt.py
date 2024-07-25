""" Tests for the apt functions. """
import os
import tempfile
from ebcl.apt import Apt


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
