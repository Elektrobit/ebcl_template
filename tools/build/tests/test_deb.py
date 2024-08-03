""" Tests for the eb functions. """
import os
import tempfile

from pathlib import Path

from ebcl.common.apt import Apt, parse_depends
from ebcl.common.deb import Package
from ebcl.common.proxy import Proxy
from ebcl.common.version import Version


class TestDeb:
    """ Tests for the deb functions. """

    apt: Apt
    proxy: Proxy

    @classmethod
    def setup_class(cls):
        """ Prepare apt repo object. """
        cls.apt = Apt()
        cls.proxy = Proxy()
        cls.proxy.add_apt(cls.apt)

    def test_download_and_extract_busybox(self):
        """ Extract data content of deb. """
        ps = self.apt.find_package('busybox-static')
        assert ps

        ps.sort()
        p = ps[-1]

        with tempfile.TemporaryDirectory() as d:
            pkg = self.proxy.download_package('amd64', p)
            assert pkg
            assert pkg.local_file
            assert os.path.isfile(pkg.local_file)

            location = pkg.extract(d)
            assert location
            assert location == d

            location = pkg.extract(None)
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

        packages = parse_depends('busybox', 'amd64')
        assert packages

        (debs, contents, missing) = proxy.download_deb_packages(
            packages=packages
        )

        assert not missing
        assert os.path.isdir(debs)
        assert contents
        assert os.path.isdir(contents)

        bb = Path(contents) / 'bin' / 'busybox'
        assert bb.is_file()

    def test_pkg_form_deb(self):
        """ Test package creation from deb files. """
        p = Package.from_deb('/path/to/my/gcab_0.7-1_i386.deb', [])
        assert p is not None
        assert p.name == 'gcab'
        assert p.version == Version('0.7-1')
        assert p.arch == 'i386'
        assert p.local_file is None

        p = Package.from_deb('/path/to/my/gcab_0.7-1_i386.dsc', [])
        assert p is None

        p = Package.from_deb('/path/to/my/gcab_0.7-1.deb', [])
        assert p is None
