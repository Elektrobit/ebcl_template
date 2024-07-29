""" Unit tests for the EBcL apt proxy. """
from pathlib import Path

from ebcl.apt import Apt
from ebcl.proxy import Proxy


class TestProxy:
    """ Unit tests for the EBcL apt proxy. """

    proxy: Proxy

    @classmethod
    def setup_class(cls):
        """ Prepare proxy. """
        cls.proxy = Proxy()

    def test_init(self):
        """ Test proxy initalization. """
        assert self.proxy.apts == [Apt()]
        assert self.proxy.cache is not None

    def test_apt_repos(self):
        """ Test apt repo handling. """
        a = Apt(
            url='ports.ubuntu.com/ubuntu-ports',
            distro='jammy',
            arch='arm64',
            components=['main', 'universe']
        )
        b = Apt(
            url='https://linux.elektrobit.com/eb-corbos-linux/1.2',
            distro='ebcl',
            arch='arm64',
            components=['prod', 'dev']
        )

        assert len(self.proxy.apts) == 1

        res = self.proxy.add_apt(Apt())
        assert not res
        assert len(self.proxy.apts) == 1

        res = self.proxy.add_apt(a)
        assert res
        assert len(self.proxy.apts) == 2

        res = self.proxy.add_apt(b)
        assert res
        assert len(self.proxy.apts) == 3

        res = self.proxy.remove_apt(a)
        assert res
        assert len(self.proxy.apts) == 2

        res = self.proxy.remove_apt(a)
        assert not res
        assert len(self.proxy.apts) == 2

    def test_find_package_busybox(self):
        """ Test that busybox-static package is found. """
        p = self.proxy.find_package('amd64', 'busybox-static')
        assert p is not None
        assert p.name == 'busybox-static'
        assert p.arch == 'amd64'

        a = Apt(
            url='http://ports.ubuntu.com/ubuntu-ports',
            distro='jammy',
            arch='arm64',
            components=['main', 'universe']
        )

        self.proxy.add_apt(a)

        p = self.proxy.find_package('arm64', 'busybox-static')
        assert p is not None
        assert p.name == 'busybox-static'
        assert p.arch == 'arm64'

    def test_find_not_existing(self):
        """ Test that tries to find a non-existing package. """
        p = self.proxy.find_package('amd64', 'some-not-existing-package')
        assert p is None

    def test_download_and_extract_linux_image(self):
        """ Extract data content of multiple debs. """
        (debs, content, missing) = self.proxy.download_deb_packages(
            'amd64',
            ['linux-image-generic']
        )

        assert not missing

        deb_path = Path(debs)
        packages = list(deb_path.glob('*.deb'))

        assert len(packages) > 0

        assert content
        content_path = Path(content)
        boot = content_path / 'boot'
        kernel_images = list(boot.glob('vmlinuz*'))

        assert len(kernel_images) > 0
