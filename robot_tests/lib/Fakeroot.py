# pylint: disable=C0103
""" Fakeroot functions for all tests. """
import logging
import os
import subprocess
import tempfile

from pathlib import Path
from subprocess import PIPE
from typing import Optional, Tuple


class Fakeroot:
    """ Fakeroot functions for all tests. """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    # fakeroot state
    fakestate: str

    def __init__(self):
        """ Create fakeroot state. """
        logging.basicConfig(level=logging.DEBUG)
        self.fakestate = tempfile.mktemp()
        Path(self.fakestate).touch()

    def __del__(self):
        """ Delete fakeroot state. """
        if self.fakestate and os.path.isfile(self.fakestate):
            # os.remove(self.fakestate)
            pass

    def run(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True
    ) -> Tuple[str, str]:
        """ Run command. """
        logging.info('CMD: %s', cmd)

        p = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            shell=True,
            stdout=PIPE,
            stderr=PIPE)

        logging.info('Command %s completed with returncode %s.',
                     cmd, p.returncode)

        pout = p.stdout.decode('utf8').strip()
        logging.info('STDOUT: %s', pout)

        perr = p.stderr.decode('utf8').strip()
        if perr:
            logging.error('STDERR: %s', perr)
        else:
            logging.info('No output on STDERR.')

        if check:
            assert p.returncode == 0

        return (pout, perr)

    def run_fake(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True
    ) -> Tuple[str, str]:
        """ Run command using fakeroot. """
        cmd = f'fakechroot fakeroot -i {self.fakestate} -s {self.fakestate} -- {cmd}'
        return self.run(
            cmd=cmd,
            cwd=cwd,
            check=check
        )

    def run_chroot(
        self,
        cmd: str,
        chroot: str,
        check=True
    ) -> Tuple[str, str]:
        """ Run command using fakechroot. """
        cmd = f'fakechroot fakeroot -i {self.fakestate} -s {self.fakestate}' \
            f' -- chroot {chroot} {cmd}'
        return self.run(
            cmd=cmd,
            check=check
        )

    def run_sudo(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True
    ) -> Tuple[str, str]:
        """ Run command using fakechroot. """
        cmd = f'sudo {cmd}'
        return self.run(
            cmd=cmd,
            cwd=cwd,
            check=check
        )

    def abs_file_should_exist(self, file: str, file_type: str = 'regular file'):
        """ Check that a file exists. """
        (out, _) = self.run_fake(cmd=f'stat -c \'%F\' {file}')
        assert out.strip() == file_type

    def abs_directory_should_exist(self, path: str):
        """ Check that a folder exists. """
        (out, _) = self.run_fake(cmd=f'stat -c \'%F\' {path}')
        assert out.strip() == 'directory'

    def abs_should_be_owned_by(self, path: str, uid: int, gid: int):
        """ Check ownership of file or dir. """
        (out, _) = self.run_fake(cmd=f'stat -c \'%u %g\' {path}')
        assert out.strip() == f'{uid} {gid}'

    def abs_should_have_mode(self, path: str, mode: int):
        """ Check ownership of file or dir. """
        (out, _) = self.run_fake(cmd=f'stat -c \'%a\' {path}')
        assert out.strip() == f'{mode}'
