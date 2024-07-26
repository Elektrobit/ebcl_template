""" Tests for the eb functions. """
import os
import tempfile

from pathlib import Path

from ebcl.apt import Apt
from ebcl.deb import extract_archive, download_deb_packages


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

            location = extract_archive(deb_path, d)
            assert location == d

            location = extract_archive(deb_path, None)
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

        (debs, contents, missing) = download_deb_packages(
            apts=[apt],
            packages=['busybox']
        )

        assert not missing
        assert os.path.isdir(debs)
        assert os.path.isdir(contents)

        bb = Path(contents) / 'bin' / 'busybox'
        assert bb.is_file()
