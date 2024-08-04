""" Fakeroot and Fakechroot helper. """
import logging
import os
import subprocess
import tempfile

from io import BufferedWriter
from pathlib import Path
from subprocess import PIPE
from typing import Tuple, Optional, Any


class Fake:
    """ Fakeroot and Fakechroot helper. """

    state: Path

    def __init__(self, state: Optional[str] = None):
        """ Set state directory. """
        if state is None:
            self.state = Path(tempfile.mktemp())
            self.state.touch()
        else:
            self.state = Path(state)

    def __del__(self):
        """ Remove state directory. """
        if self.state:
            if os.path.isfile(self.state):
                os.remove(self.state)

    def run_no_fake(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        stdout: Optional[BufferedWriter] = None,
        check=True
    ) -> Tuple[Optional[str], str, int]:
        """ Run a command. """
        logging.info('Running command: %s', cmd)

        out: Any
        if stdout is None:
            out = PIPE
        else:
            out = stdout

        p = subprocess.run(
            cmd,
            check=False,
            shell=True,
            stdout=out,
            stderr=PIPE,
            cwd=cwd
        )

        if stdout is None:
            pout = p.stdout.decode('utf8')
            if pout.strip():
                logging.info('STDOUT: %s', pout)
        else:
            pout = None

        perr = p.stderr.decode('utf8')
        if perr.strip():
            logging.error('%s has stderr output.\nSTDERR: %s', cmd, perr)

        if p.returncode != 0:
            logging.info('Returncode: %s', p.returncode)

        if check:
            assert p.returncode == 0

        return (pout, perr, p.returncode)

    def run(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        stdout: Optional[BufferedWriter] = None,
        check=True
    ) -> Tuple[Optional[str], str, int]:
        """ Run a command using fakeroot. """
        return self.run_no_fake(
            cmd=f'fakechroot fakeroot -i {self.state} -s {self.state} -- {cmd}',
            cwd=cwd,
            stdout=stdout,
            check=check
        )

    def run_chroot(self, cmd: str, chroot: str, check=True) -> Tuple[str, str, int]:
        """ Run a command using fakechroot. """
        (out, err, returncode) = self.run_no_fake(
            cmd=f'fakechroot fakeroot -i {self.state} -s {self.state} -- chroot {chroot} {cmd}',
            check=check
        )

        if out is None:
            out = ''

        return (out, err, returncode)

    def run_sudo_chroot(self, cmd: str, chroot: str, check=True) -> Tuple[str, str, int]:
        """ Run a command using sudo and chroot. """
        (out, err, returncode) = self.run_no_fake(
            cmd=f'sudo chroot {chroot} {cmd}',
            check=check
        )

        if out is None:
            out = ''

        return (out, err, returncode)

    def run_sudo(
            self, cmd: str,
            cwd: Optional[str] = None,
            stdout: Optional[BufferedWriter] = None,
            check=True
    ) -> Tuple[Optional[str], str, int]:
        """ Run a command using sudo. """
        return self.run_no_fake(
            cmd=f'sudo bash -c "{cmd}"',
            cwd=cwd,
            stdout=stdout,
            check=check
        )
