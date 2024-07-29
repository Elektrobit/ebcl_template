""" Tests for the eb functions. """
import os
import tempfile

from pathlib import Path

from ebcl.apt import Apt
from ebcl.deb import Package
from ebcl.proxy import Proxy


class TestDeb:
    """ Tests for the deb functions. """

    apt: Apt

    @classmethod
    def setup_class(cls):
        """ Prepare apt repo object. """
        cls.apt = Apt()

    def test_download_and_extract_busybox(self):
        """ Extract data content of deb. """
        p = self.apt.find_package('busybox-static')
        assert p is not None

        with tempfile.TemporaryDirectory() as d:
            deb_path = p.download(d)
            assert deb_path is not None

            assert os.path.isfile(deb_path)

            location = p.extract(d)
            assert location == d

            location = p.extract(None)
            assert location is not None
            assert os.path.isdir(os.path.join(location))
            assert os.path.isfile(os.path.join(
                location, 'bin', 'busybox'))

    def test_download_deb_packages(self):
        """ Test download busybox and depends. """
        apt = Apt(
            url='http://archive.ubuntu.com/ubuntu',
            distro='jammy',
            components=['main', 'universe'],
            arch='amd64'
        )

        proxy = Proxy()
        proxy.add_apt(apt)

        (debs, contents, missing) = proxy.download_deb_packages(
            arch='amd64',
            packages=['busybox']
        )

        assert not missing
        assert os.path.isdir(debs)
        assert contents
        assert os.path.isdir(contents)

        bb = Path(contents) / 'bin' / 'busybox'
        assert bb.is_file()

    def test_pkg_form_deb(self):
        """ Test package creation from deb files. """
        p = Package.from_deb('/path/to/my/gcab_0.7-1_i386.deb')
        assert p is not None
        assert p.name == 'gcab'
        assert p.version == '0.7-1'
        assert p.arch == 'i386'
        assert p.local_file is None

        p = Package.from_deb('/path/to/my/gcab_0.7-1_i386.dsc')
        assert p is None

        p = Package.from_deb('/path/to/my/gcab_0.7-1.deb')
        assert p is None
