""" Test library for the initrd generator. """
import logging
import os
import shutil
import tempfile

from subprocess import Popen, PIPE


class Initrd:
    """ Test library for the initrd generator. """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    slash_init: str
    root: str
    target: str

    def build_initrd(
        self,
        config: str | None = None,
        generator: str | None = None
    ):
        """ Build the initrd image. """
        if config is None:
            config = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'data', 'initrd.yaml'))
        if generator is None:
            generator = "/workspace/tools/bin/initrd_generator"

        self.target = tempfile.mkdtemp()
        logging.info('Target directory: %s', self.target)

        p = Popen(
            [generator, config, self.target],
            stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        logging.info('build STDOUT: %s', stdout.decode(encoding='utf8'))
        logging.info('build STDERR: %s', stderr.decode(encoding='utf8'))
        assert p.returncode == 0

    def _unpack(self, arch):
        """ Unpack the initrd image. """
        os.makedirs(self.target, exist_ok=True)
        p = Popen(["cpio", "-di", "-F", arch, "-D", self.target],
                  stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        logging.info('unpack STDERR: %s', stderr.decode(encoding='utf8'))
        logging.info('unpack STDOUT: %s', stdout.decode(encoding='utf8'))
        assert p.returncode == 0

    def load(self):
        """ Unpack the initrd and read the init script. """
        path = os.path.join(self.target, 'initrd.img')
        self._unpack(path)
        self.slash_init = open(os.path.join(
            self.target, 'init'), encoding='utf8').read()
        logging.info('Init: %s', self.slash_init)

    def cleanup(self):
        """ Remove generated artefacts. """
        shutil.rmtree(self.target)

    def file_should_exist(self, path: str):
        """ Check that a file exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        file = os.path.join(self.target, path)
        assert os.path.isfile(file)

    def directory_should_exist(self, path: str):
        """ Check that a folder exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        d = os.path.join(self.target, path)
        assert os.path.isdir(d)

    def module_should_be_loaded(self, module_name: str):
        """ Ensure that the given module is loaded. """
        assert self.slash_init is not None
        assert f'modprobe {module_name}' in self.slash_init

    def device_should_be_mounted(self, device: str, mountpoint: str):
        """ Ensure that the given device is the default as root. """
        assert self.slash_init is not None
        assert f'root={device}' in self.slash_init
        assert f'mount $root {mountpoint}' in self.slash_init
