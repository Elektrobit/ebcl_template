# pylint: disable=C0103
""" Fakeroot functions for all tests. """
import logging
import os
import subprocess
import tempfile

from pathlib import Path
from subprocess import PIPE, CalledProcessError
from typing import Optional, Tuple


class Fakeroot:
    """ Fakeroot functions for all tests. """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        """ Create fakeroot state. """
        logging.basicConfig(level=logging.DEBUG)
        self.fakestate = tempfile.mktemp()
        Path(self.fakestate).touch()

    def __del__(self):
        """ Delete fakeroot state. """
        if self.fakestate and os.path.isfile(self.fakestate):
            os.remove(self.fakestate)

    def run(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True,
        capture_output=True,
        stderr_as_info=False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """ Run command. """
        logging.info('CMD: %s', cmd)

        pout = None
        perr = None

        try:
            p = subprocess.run(
                cmd,
                cwd=cwd,
                check=False,
                shell=True,
                stdout=PIPE if capture_output else None,
                stderr=PIPE if capture_output else None)

            logging.info('Command %s completed with returncode %s.',
                        cmd, p.returncode)


            if p.stdout:
                pout = p.stdout.decode('utf8', errors='ignore').strip()
                logging.info('STDOUT: %s', pout)
            else:
                logging.info('No STDOUT capturing.')

            if p.stderr:
                perr = p.stderr.decode('utf8', errors='ignore').strip()
                if perr:
                    if stderr_as_info:
                        logging.info('STDERR: %s', perr)
                    else:
                        logging.error('STDERR: %s', perr)
                else:
                    logging.info('No output on STDERR.')
            else:
                logging.info('No STDOUT capturing.')
        except CalledProcessError as e:
            if check:
                raise e

        return (pout, perr)

    def run_fake(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True
    ) -> Tuple[Optional[str], Optional[str]]:
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
    ) -> Tuple[Optional[str], Optional[str]]:
        """ Run command using fakechroot. """
        cmd = f'sudo chroot {chroot} {cmd}'
        return self.run(
            cmd=cmd,
            check=check
        )

    def run_sudo(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        check=True
    ) -> Tuple[Optional[str], Optional[str]]:
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
        assert out
        assert out.strip() == file_type

    def abs_directory_should_exist(self, path: str):
        """ Check that a folder exists. """
        (out, _) = self.run_fake(cmd=f'stat -c \'%F\' {path}')
        assert out
        assert out.strip() == 'directory'

    def abs_should_be_owned_by(self, path: str, uid: int, gid: int):
        """ Check ownership of file or dir. """
        (out, _) = self.run_fake(cmd=f'stat -c \'%u %g\' {path}')
        assert out
        assert out.strip() == f'{uid} {gid}'

    def abs_should_have_mode(self, path: str, mode: int):
        """ Check ownership of file or dir. """
        (out, _) = self.run_fake(cmd=f'stat -c \'%a\' {path}')
        assert out
        assert out.strip() == f'{mode}'
