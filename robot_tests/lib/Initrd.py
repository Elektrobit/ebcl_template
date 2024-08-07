"""
Module to handle initrd image created by create_initrd.py script,
and to check its contents.
"""
import tempfile
import os
import re
from subprocess import Popen, DEVNULL, PIPE


class Initrd:
    """
    Class to build/create, extract/unpack,
    check files and directories, check the init script
    of the image created by create_initrd.py script
    """
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self) -> None:
        self.slash_init = None
        self.root = None

    def build_initrd(self, config: str, target: str, generator=None):
        """
        Build an initrd image with create_initrd.py script
        """
        if generator is None:
            generator = "tools/initrd/create_initrd.py"

        p = Popen([generator, config, target], stdout=DEVNULL, stderr=PIPE)
        _, stderr = p.communicate()
        if p.returncode != 0:
            raise p.CalledProcessError(p.returncode, p.args, p.stdout,
                                       stderr)

    def unpack(self, arch, target=None) -> str:
        """
        Extract an initrd image
        """
        if target is None:
            target = tempfile.gettempdir() + "/initrd_unpack"
        os.makedirs(target, exist_ok=True)
        p = Popen(["cpio", "-di", "-F", arch, "-D", target],
                  stdout=DEVNULL, stderr=PIPE)
        _, stderr = p.communicate()
        if p.returncode != 0:
            raise p.CalledProcessError(p.returncode, p.args, p.stdout,
                                       stderr)

        print(Popen(["tree", target], stdout=PIPE).communicate()[0].decode())
        return target

    def load(self, path: str):
        """
        Extract an initrd image, and print its init script
        """
        self.root = self.unpack(path)
        self.slash_init = open(self.root + "/init", encoding="UTF-8").read()
        print(self.slash_init)

    def file_should_exist(self, path: str):
        """
        Check that file exists in the extracted initrd image
        """
        if not os.path.exists(self.root + "/" + path):
            raise FileNotFoundError(f"Directory \"{path}\" does not exist")

        if os.path.isdir(self.root + "/" + path):
            raise IsADirectoryError(f"\"{path}\" exists but is a directory")

    def directory_should_exist(self, path: str):
        """
        Check that directory exists in the extracted initrd image
        """
        if not os.path.isdir(self.root + "/" + path):
            raise FileNotFoundError(f"Directory \"{path}\" does not exist")

    def module_should_be_loaded(self, module_name: str):
        """
        Check that module probe command exists in the init script
        """
        r = re.compile(f"\\w*modprobe {module_name}")
        for line in self.slash_init.splitlines():
            if r.match(line):
                return
        raise RuntimeError(f"Module \"{module_name}\" is not loaded")

    def device_should_be_mounted(self, device: str):
        """
        Check that device mount command exists in the init script
        """
        r = re.compile(f"\\w*mount.*{device}")
        for line in self.slash_init.splitlines():
            if r.match(line):
                return
        raise RuntimeError(f"Device \"{device}\" is not loaded")
