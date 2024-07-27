""" Fakeroot and Fakechroot helper. """
import logging
import os
import subprocess
import tempfile

from io import FileIO
from pathlib import Path
from subprocess import PIPE
from typing import Tuple, Optional


class Fake:
    """ Fakeroot and Fakechroot helper. """

    state: Path

    def __init__(self, state: str = None):
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

    def run(
        self,
        cmd: str,
        cwd: Optional[str] = None,
        stdout: Optional[FileIO] = None,
        check=True
    ) -> Tuple[None | str, str]:
        """ Run a command using fakeroot. """
        logging.info('Running command: %s', cmd)

        out: int | FileIO
        if stdout is None:
            out = PIPE
        else:
            out = stdout

        p = subprocess.run(
            f'fakechroot fakeroot -i {self.state} -s {self.state} -- {cmd}',
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
            logging.info('STDERR: %s', perr)

        if check:
            assert p.returncode == 0

        return (pout, perr)

    def run_chroot(self, cmd: str, chroot: str, check=True) -> Tuple[str, str]:
        """ Run a command using fakechroot. """
        logging.info('Running command \'%s\' in chroot %s.', cmd, chroot)

        p = subprocess.run(
            f'fakechroot fakeroot -i {self.state} -s {self.state} -- chroot {chroot} {cmd}',
            check=False,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout = p.stdout.decode('utf8')
        stderr = p.stderr.decode('utf8')

        if stdout.strip():
            logging.info('STDOUT: %s', stdout)
        if stderr.strip():
            logging.info('STDERR: %s', stderr)

        if check:
            assert p.returncode == 0

        return (stdout, stderr)

    def run_sudo_chroot(self, cmd: str, chroot: str, check=True) -> Tuple[str, str]:
        """ Run a command using sudo and chroot. """
        logging.info('Running command \'%s\' in sudo chroot %s.', cmd, chroot)

        p = subprocess.run(
            f'sudo chroot {chroot} {cmd}',
            check=False,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout = p.stdout.decode('utf8')
        stderr = p.stderr.decode('utf8')

        if stdout.strip():
            logging.info('STDOUT: %s', stdout)
        if stderr.strip():
            logging.info('STDERR: %s', stderr)

        if check:
            assert p.returncode == 0

        return (stdout, stderr)

    def run_sudo(
            self, cmd: str,
            cwd: Optional[str] = None,
            stdout: Optional[FileIO] = None,
            check=True
    ) -> Tuple[Optional[str], str]:
        """ Run a command using sudo. """
        logging.info('Running command \'%s\' using sudo.', cmd)

        out: int | FileIO
        if stdout is None:
            out = PIPE
        else:
            out = stdout

        p = subprocess.run(
            f'sudo bash -c "{cmd}"',
            check=False,
            shell=True,
            stdout=out,
            stderr=subprocess.PIPE,
            cwd=cwd)

        if stdout is None:
            pout = p.stdout.decode('utf8')
            if pout.strip():
                logging.info('STDOUT: %s', pout)
        else:
            pout = None

        perr = p.stderr.decode('utf8')
        if perr.strip():
            logging.info('STDERR: %s', perr)

        if check:
            assert p.returncode == 0

        return (pout, perr)
