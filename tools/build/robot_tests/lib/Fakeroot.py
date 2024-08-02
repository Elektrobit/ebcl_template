""" Fakeroot functions for all tests. """
import logging
import os
import subprocess
import tempfile

from subprocess import PIPE
from typing import Optional, Tuple


class Fakeroot:
    """ Fakeroot functions for all tests. """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    # fakeroot state
    fakestate: str

    def __init__(self):
        """ Create fakeroot state. """
        self.fakestate = tempfile.mktemp()

    def __del__(self):
        """ Delete fakeroot state. """
        if self.fakestate and os.path.isfile(self.fakestate):
            # os.remove(self.fakestate)
            pass

    def run_no_fake(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True
    ) -> Tuple[str, str]:
        """ Run command using fakeroot. """
        logging.info('CMD: %s', cmd)

        p = subprocess.run(
            cmd,
            cwd=cwd,
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

    def run(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True
    ) -> Tuple[str, str]:
        """ Run command using fakeroot. """
        cmd = f'fakechroot fakeroot -i {self.fakestate} -s {self.fakestate} -- {cmd}'
        return self.run_no_fake(
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
        return self.run_no_fake(
            cmd=cmd,
            check=check
        )

    def abs_file_should_exist(self, file: str, file_type: str = 'regular file'):
        """ Check that a file exists. """
        (out, _) = self.run(cmd=f'stat -c \'%F\' {file}')
        assert out.strip() == file_type

    def abs_directory_should_exist(self, path: str):
        """ Check that a folder exists. """
        (out, _) = self.run(cmd=f'stat -c \'%F\' {path}')
        assert out.strip() == 'directory'

    def abs_should_be_owned_by(self, path: str, uid: int, gid: int):
        """ Check ownership of file or dir. """
        (out, _) = self.run(cmd=f'stat -c \'%u %g\' {path}')
        assert out.strip() == f'{uid} {gid}'

    def abs_should_have_mode(self, path: str, mode: int):
        """ Check ownership of file or dir. """
        (out, _) = self.run(cmd=f'stat -c \'%a\' {path}')
        assert out.strip() == f'{mode}'
