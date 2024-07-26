""" Test library for the initrd generator. """
import logging
import os
import shutil
import subprocess
import tempfile

from subprocess import Popen, PIPE
from typing import Tuple


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

        cmd = f'{generator} {config} {self.target}'
        (out, err) = self._run(cmd)

        logging.info('STDOUT: %s', out)
        logging.info('STDERR: %s', err)

    def _unpack(self, arch):
        """ Unpack the initrd image. """
        os.makedirs(self.target, exist_ok=True)

        cmd = f'cpio -di -F {arch} -D {self.target}'
        (out, err) = self._run_sudo(cmd)

        logging.info('STDOUT: %s', out)
        logging.info('STDERR: %s', err)

    def _run_sudo(self, cmd: str, check=True) -> Tuple[str, str]:
        """ Run command using sudo. """
        return self._run(f'sudo bash -c "{cmd}"', check=check)

    def _run(self, cmd: str, check=True) -> Tuple[str, str]:
        """ Run command. """
        logging.info('CMD: %s', cmd)

        p = subprocess.run(
            cmd,
            check=True,
            shell=True,
            stdout=PIPE,
            stderr=PIPE)

        pout = p.stdout.decode('utf8')
        logging.info('STDOUT: %s', pout)

        perr = p.stderr.decode('utf8')
        logging.info('STDERR: %s', perr)

        if check:
            assert p.returncode == 0

        return (pout, perr)

    def load(self):
        """ Unpack the initrd and read the init script. """
        path = os.path.join(self.target, 'initrd.img')
        self._unpack(path)
        self.slash_init = open(os.path.join(
            self.target, 'init'), encoding='utf8').read()
        logging.info('Init: %s', self.slash_init)

    def cleanup(self):
        """ Remove generated artefacts. """
        return
        (out, err) = self._run_sudo(f'sudo rm -rf "{self.target}"')

        logging.info('STDOUT: %s', out)
        logging.info('STDERR: %s', err)

    def file_should_exist(self, path: str, file_type: str = 'regular file'):
        """ Check that a file exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        file = os.path.join(self.target, path)

        # Will return error code != 0 if file not exists.
        self._run_sudo(f'ls -lah {file}')

        (out, _) = self._run_sudo(f'stat -c \'%F\' {file}')
        assert out.strip() == file_type

    def directory_should_exist(self, path: str):
        """ Check that a folder exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        d = os.path.join(self.target, path)

        # Will return error code != 0 if file not exists.
        self._run_sudo(f'ls -lah {d}')

        (out, _) = self._run_sudo(f'stat -c \'%F\' {d}')
        assert out.strip() == 'directory'

    def module_should_be_loaded(self, module_name: str):
        """ Ensure that the given module is loaded. """
        assert self.slash_init is not None
        assert f'modprobe {module_name}' in self.slash_init

    def device_should_be_mounted(self, device: str, mountpoint: str):
        """ Ensure that the given device is the default as root. """
        assert self.slash_init is not None
        assert f'root={device}' in self.slash_init
        assert f'mount $root {mountpoint}' in self.slash_init
