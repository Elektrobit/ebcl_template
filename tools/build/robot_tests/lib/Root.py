""" Test library for the root generator. """
import logging
import os
import tempfile

from typing import Optional, Tuple

from Fakeroot import Fakeroot


class Root:
    """ Test library for the root generator. """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    # directory for initrd build output
    target: str
    # helper
    fake = Fakeroot()

    def __init__(self):
        """ Init Python logging. """
        logging.basicConfig(level=logging.DEBUG)

    def build_root(
        self,
        config: Optional[str] = None,
        generator: Optional[str] = None
    ):
        """ Build the root archive. """
        if config is None:
            config = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'data', 'root.yaml'))
        if generator is None:
            generator = "root_generator"

        self.target = tempfile.mkdtemp()
        logging.info('Target directory: %s', self.target)

        cmd = f'bash -c "source /build/venv; {generator} {config} {self.target}"'
        self.fake.run_no_fake(cmd)

    def _unpack(self):
        """ Unpack the boot tar. """
        archive = os.path.join(self.target, 'ubuntu.tar')

        logging.info('Root archive: %s', archive)
        logging.info('Work folder: %s', self.target)

        assert os.path.isfile(archive)

        self._run(f'tar xf {archive}')
        self._run('ls -lah')

    def _run(self, cmd: str, check=True) -> Tuple[str, str]:
        """ Run command using fakeroot. """

        return self.fake.run(
            cmd=cmd,
            cwd=self.target,
            check=check
        )

    def load(self):
        """ Unpack the initrd and read the init script. """
        self._unpack()

    def cleanup(self):
        """ Remove generated artefacts. """
        # self._run(f'rm -rf {self.target}')

    def file_should_exist(self, path: str, file_type: str = 'regular file'):
        """ Check that a file exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        file = os.path.join(self.target, path)

        self.fake.abs_file_should_exist(file, file_type)

    def directory_should_exist(self, path: str):
        """ Check that a folder exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        d = os.path.join(self.target, path)

        self.fake.abs_directory_should_exist(d)

    def should_have_mode(self, path: str, mode: str):
        """ Check that a file exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        path = os.path.join(self.target, path)

        self.fake.abs_should_have_mode(
            path=path,
            mode=int(mode))

    def should_be_owned_by(self, path: str, uid: str, gid: str):
        """ Check that a file exists. """
        assert self.target is not None
        if path.startswith('/'):
            path = path[1:]
        path = os.path.join(self.target, path)

        self.fake.abs_should_be_owned_by(
            path=path,
            uid=int(uid),
            gid=int(gid))
