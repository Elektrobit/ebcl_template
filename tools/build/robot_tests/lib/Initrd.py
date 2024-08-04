""" Test library for the initrd generator. """
import logging
import tempfile
import os

from typing import Tuple, Optional

from Fakeroot import Fakeroot


class Initrd:
    """ Test library for the initrd generator. """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    # content of init script
    init: str
    # directory for initrd build output
    target: str
    # helper
    fake = Fakeroot()

    def __init__(self):
        """ Init Python logging. """
        logging.basicConfig(level=logging.DEBUG)

    def build_initrd(
        self,
        config: Optional[str] = None,
        generator: Optional[str] = None
    ):
        """ Build the initrd imastat -c '%F' /tmp/tmphvx3j23p/root/dummyge. """
        if config is None:
            config = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'data', 'initrd.yaml'))
        elif not config.startswith('/'):
            config = os.path.abspath(os.path.join(
                os.path.dirname(__file__), config))

        if generator is None:
            generator = "initrd_generator"

        self.target = tempfile.mkdtemp()
        logging.info('Target directory: %s', self.target)

        cmd = f'bash -c "source /build/venv; {generator} {config} {self.target}"'
        self.fake.run_no_fake(cmd)

    def _unpack(self, arch):
        """ Unpack the initrd image. """
        os.makedirs(self.target, exist_ok=True)

        cmd = f'cpio -di -F {arch} -D {self.target}'
        self._run(cmd)

    def _run(self, cmd: str, check=True) -> Tuple[str, str]:
        """ Run command using fakeroot. """
        return self.fake.run(
            cmd=cmd,
            cwd=self.target,
            check=check
        )

    def load(self):
        """ Unpack the initrd and read the init script. """
        path = os.path.join(self.target, 'initrd.img')
        self._unpack(path)
        self.init = open(os.path.join(
            self.target, 'init'), encoding='utf8').read()
        logging.info('Init: %s', self.init)

    def cleanup(self):
        """ Remove generated artefacts. """
        self._run(f'rm -rf {self.target}')

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

    def module_should_be_loaded(self, module_name: str):
        """ Ensure that the given module is loaded. """
        assert self.init is not None
        assert f'modprobe {module_name}' in self.init

    def device_should_be_mounted(self, device: str, mountpoint: str):
        """ Ensure that the given device is the default as root. """
        assert self.init is not None
        assert f'root={device}' in self.init
        assert f'mount $root {mountpoint}' in self.init

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
