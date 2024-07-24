""" Tests for the apt functions. """
import os
import tempfile
from ebcl.apt import Apt


class TestApt:
    """ Tests for the apt functions. """

    cls: Apt

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
            success = p.download(d)
            assert success is True

            local_filename = p.file_url.split('/')[-1]
            assert os.path.isfile(os.path.join(d, local_filename))
