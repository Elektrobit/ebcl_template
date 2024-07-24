""" Tests for the eb functions. """
import os
import tempfile
from ebcl.apt import Apt
from ebcl.deb import extract_archive


class TestDeb:
    """ Tests for the deb functions. """

    cls: Apt

    @classmethod
    def setup_class(cls):
        """ Prepare apt repo object. """
        cls.apt = Apt()

    def test_download_and_extract_busybox(self):
        """ Search busybox package in default apt repository. """
        p = self.apt.find_package('busybox-static')
        assert p is not None

        with tempfile.TemporaryDirectory() as d:
            deb_path = p.download(d)
            assert deb_path is not None

            assert os.path.isfile(deb_path)

            location = extract_archive(deb_path, d)
            assert location == d

            location = extract_archive(deb_path, None)
            assert location is not None
            assert os.path.isdir(location)
            assert os.path.isfile(os.path.join(location, 'debian-binary'))
