""" Tests for the fake functions. """
import os
import shutil
import tempfile

from ebcl.apt import Apt
from ebcl.fake import Fake
from ebcl.proxy import Proxy


class TestFake:
    """ Tests for the apt functions. """

    fake: Fake
    apt: Apt

    @classmethod
    def setup_class(cls):
        """ Prepare apt repo object. """
        cls.fake = Fake()
        cls.apt = Apt()

    def test_run(self):
        """ Run a command using fakeroot. """
        (stdout, stderr) = self.fake.run('id')
        assert stdout is not None
        assert 'uid=0(root)' in stdout
        assert 'gid=0(root)' in stdout
        assert not stderr.strip()

    def test_run_chroot(self):
        """ Run a command using fakechroot. """
        # Prepare fakeroot
        # Get busybox
        p = self.apt.find_package('busybox-static')
        assert p is not None

        chroot = tempfile.mkdtemp()

        deb_path = p.download(chroot)
        assert deb_path is not None
        assert os.path.isfile(deb_path)

        p.extract(chroot)

        # Prepare dev folder
        (_stdout, stderr) = self.fake.run_chroot(
            'busybox mkdir -p dev', chroot)
        assert not stderr.strip()

        # Check folder
        (stdout, stderr) = self.fake.run_chroot(
            'busybox stat -c \'%u %g\' /dev', chroot)
        assert stdout.strip() == '0 0'
        assert not stderr.strip()

        self.fake.run_sudo(f'rm -rf {chroot}')

    def test_run_sudo_chroot(self):
        """ Run a command using fakechroot. """
        # Prepare fakeroot
        # Get busybox
        p = self.apt.find_package('busybox-static')
        assert p is not None

        chroot = tempfile.mkdtemp()

        deb_path = p.download(chroot)
        assert deb_path is not None
        assert os.path.isfile(deb_path)

        p.extract(chroot)

        # Install busybox
        (_stdout, stderr) = self.fake.run_sudo_chroot(
            '/bin/busybox --install -s /bin', chroot)
        assert not stderr.strip()

        # Prepare dev folder
        (_stdout, stderr) = self.fake.run_sudo_chroot('mkdir -p dev', chroot)
        assert not stderr.strip()

        # Check folder
        (stdout, stderr) = self.fake.run_sudo_chroot(
            'stat -c \'%u %g\' /dev', chroot)
        assert stdout.strip() == '0 0'
        assert not stderr.strip()

        # Create device node
        (_stdout, stderr) = self.fake.run_sudo_chroot(
            'mknod -m 777 /dev/console c 1234 1234', chroot)
        assert not stderr.strip()

        # Check device node
        (stdout, stderr) = self.fake.run_sudo_chroot(
            'stat -c \'%A %u %g\' /dev/console', chroot)
        assert stdout.strip() == 'crwxrwxrwx 0 0'
        assert not stderr.strip()

        self.fake.run_sudo(f'rm -rf {chroot}')

    def test_mix(self):
        """ Test mix of fakeroot and fakechroot. """
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
        assert contents

        shutil.rmtree(debs)

        (out, err) = self.fake.run_chroot('/bin/busybox id', contents)
        assert err == ''
        assert 'uid=0' in out
        assert 'gid=0' in out

        (out2, err) = self.fake.run(cmd=f'file {contents}')
        assert err == ''
        assert out2 is not None
        assert 'directory' in out2

        (out, err) = self.fake.run_chroot(
            '/bin/busybox ls -lah /bin/busybox', contents)
        assert err == ''
        assert '/bin/busybox' in out

        shutil.rmtree(contents)
