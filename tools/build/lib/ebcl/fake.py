""" Fakeroot and Fakechroot helper. """
import logging
import shutil
import subprocess
import tempfile

from pathlib import Path
from typing import Tuple


class Fake:
    """ Fakeroot and Fakechroot helper. """

    state: Path

    def __init__(self, state: str | None = None):
        """ Set state directory. """
        if state is None:
            self.state = Path(tempfile.mktemp())
            self.state.touch()
        else:
            self.state = Path(state)

    def __del__(self):
        """ Remove state directory. """
        shutil.rmtree(self.state)

    def run(self, cmd: str, check=True) -> Tuple[str, str]:
        """ Run a command using fakeroot. """
        logging.info('Running command: %s', cmd)

        p = subprocess.run(
            f'fakeroot -i {self.state} -s {self.state} -- {cmd}',
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

    def run_chroot(self, cmd: str, chroot: str, check=True) -> Tuple[str, str]:
        """ Run a command using fakechroot. """
        logging.info('Running command \'%s\' in chroot %s.', cmd, chroot)

        p = subprocess.run(
            f'fakechroot fakeroot -i {self.state} -s {self.state} -- chroot {chroot} {cmd}',
            check=True,
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
            check=True,
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

    def run_sudo(self, cmd: str, check=True) -> Tuple[str, str]:
        """ Run a command using sudo. """
        logging.info('Running command \'%s\' using sudo.', cmd)

        p = subprocess.run(
            f'sudo {cmd}',
            check=True,
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
