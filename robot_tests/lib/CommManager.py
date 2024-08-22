# pylint: disable=C0103
"""
Allows Robot to communicate with a physical or virtual target
while abstracting away the concrete communication channel
"""
import logging
import os
import re
import time

from typing import Any, Optional
from uuid import uuid4

from interfaces.ssh import SshInterface
from interfaces.tmux import TmuxConsole
from interfaces.process import ShellSubprocess


class InvalidImageError(Exception):
    """ Raised if given QEMU image is invalid. """


class CommManager:
    """
    Provides an abstracted communication interface to a target.

    That target might be physical or virtual and might communicate over any
    interface (serial, ssh, etc.). Tests must not make assumptions about either
    and only use methods provided here, not in the specific interface classes.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    interface: Any

    # pylint: disable=W1113
    # Robot requires default values for all args
    def __init__(self, mode="SSH", *args) -> None:
        logging.basicConfig(level=logging.DEBUG)

        logging.info('Setting up CommManager with interface %s...', mode)

        self.mode = mode
        match mode:
            case "SSH":
                self.interface = SshInterface(*args)
            case "Serial":
                self.interface = TmuxConsole(*args)
            case "Process":
                self.interface = ShellSubprocess(*args)
            case x:
                raise ValueError(
                    f"Unknown communication interface '{x}' specified")

    def connect(self):
        """
        Perform any actions needed to establish the actual connection to the target
        """
        logging.info('Connect to interface %s...', self.interface)
        self.interface.connect()

    def disconnect(self):
        """
        Perform any actions needed to stop the actual connection to the target
        """
        logging.info('Disconnect from interface %s...', self.interface)
        self.interface.disconnect()

    def send_message(self, message: str):
        """
        Send a message over the interface

        Appends a newline to the end iff none is present
        """
        logging.info('Send message %s to interface %s...',
                     message, self.interface)
        self.interface.send_message(message)

    def send_key(self, key: str):
        """
        Send a keystroke over the interface
        """
        logging.info('Send key %s to interface %s...',
                     key, self.interface)
        self.interface.send_key(key)

    def send_keys(self, keys: str):
        """
        Send the given keys over the inverface.
        """
        logging.info('Send keys %s to interface %s...',
                     keys, self.interface)
        self.interface.send_keys(keys)

    def wait_for_line_containing(self, search: str, timeout: int = -1) -> bool:
        """
        Ingest lines until a matching line is found
        """
        logging.info('Waiting for line containing %s on interface %s...',
                     search, self.interface)

        start_time = time.time()
        while True:
            if timeout > 0 and time.time() - start_time >= timeout:
                return False

            r = self.interface.next_line(timeout=timeout)
            if not r:
                continue

            if search in r:
                logging.info('Matching line found: %s', r)
                return True

    def wait_for_line(self, line: str, timeout: int = -1) -> bool:
        """
        Ingest lines until a matching line is found
        Ignores leading and trailing whitespace
        """
        logging.info('Waiting for line %s on interface %s...',
                     line, self.interface)

        start_time = time.time()
        while True:
            if timeout > 0 and time.time() - start_time >= timeout:
                return False

            r = self.interface.next_line(timeout=timeout)
            if not r:
                continue

            if line.strip() == r.strip():
                logging.info('Matching line found...')
                return True

    def wait_for_line_exact(self, line: str, timeout: int = -1) -> bool:
        """
        Ingest lines until a matching line is found
        Does NOT ignores leading and trailing whitespace
        """
        start_time = time.time()
        while True:
            if timeout > 0 and time.time() - start_time >= timeout:
                return False

            r = self.interface.next_line(timeout=timeout)
            if not r:
                continue

            if line == r:
                logging.info('Matching line found...')
                return True

    def wait_for_regex(self, regex: str, timeout: int = -1) -> Optional[re.Match]:
        """
        Ingest lines until a line matching the regex is found.

        Does NOT ignore leading and trailing whitespace,
        the regex needs to match the trailing newline
        """
        rg = re.compile(regex)
        logging.info('Waiting for regex %s...', rg)

        start_time = time.time()
        while True:
            if timeout > 0 and time.time() - start_time >= timeout:
                return None

            r = self.interface.next_line(timeout=timeout)
            if not r:
                continue

            m = rg.match(r)
            if m:
                return m

    def execute(self, message, timeout: int = -1) -> Optional[str]:
        """
        Read all lines produced by the given message
        """
        terminator = uuid4()
        ter = str(terminator)

        logging.info('Executing %s (ter: %s)...', message, ter)

        logging.info('Clearing old output...')

        self.clear_lines()
        time.sleep(0.2)

        logging.info('Running command %s...', message)

        self.send_message(message + "; echo " + ter)

        buf = ""
        start_time = time.time()
        while True:
            if timeout > 0 and time.time() - start_time >= timeout:
                logging.error(
                    'Execute "%s" failed because of timeout %s!', message, timeout)
                return None

            line = self.interface.next_line(timeout=timeout)
            if not line:
                continue

            if f'; echo {ter}' in line:
                # Skip line if command is echoed.
                continue

            if ter in line:
                logging.info('Line %s matches terminator...', line)
                buf += line  # do not loose output if not line break
                return buf

            buf += line

    def read_line(self) -> str:
        """ Read the next line. """
        return self.interface.next_line()

    def login_to_vm(self, user: str = 'root', password: str = 'linux',
                    shell_prompt: str = '.*#.*', timeout: int = 120) -> bool:
        """ Login to VM. """
        logging.info("Waiting for login prompt...")

        time.sleep(1)  # Give other processes and thread some time do work
        self.clear_lines()  # Delete all the output bevor trying to login

        self.send_keys('\n')  # Press return to show the login prompt

        m = self.wait_for_regex(".*login:.*", timeout=timeout)
        if not m:
            logging.info("Trying to get login prompt by pressing enter...")
            for i in range(0, 30):
                logging.info('Try %d to get login prompt...', i)
                self.send_keys('\n')
                m = self.wait_for_regex(".*login:.*", timeout=1)
                if m:
                    logging.info('Login prompt detected.')
                    break

        if not m:
            return False

        logging.info("Logging in with default credentials...")
        self.send_message(user)

        time.sleep(5)  # Give some time to process user

        self.send_message(password)

        logging.info("Trying to get shell prompt...")

        for i in range(0, 30):
            logging.info('Try %d to get shell prompt...', i)
            self.send_keys('\n')
            m = self.wait_for_regex(shell_prompt, timeout=1)
            if m:
                return True

        return False

    def clear_lines(self):
        """
        Clear all the output lines.
        """
        self.interface.clear_lines()

    def run_qemu_image(self, image: str, arch: Optional[str] = None,
                       kernel_commandline: Optional[str] = None, memory: str = '256',
                       images_folder: str = '/workspace/results/images'):
        """ Run a QEMU image using the given communication interface. """
        image = os.path.join(images_folder, image)

        logging.info('Running image %s...', image)

        console = ''
        arch_options = ''
        if not arch:
            if 'aarch64' in image:
                arch = 'aarch64'
                console = 'console=ttyAMA0,115200n8'
                arch_options = '    -machine virt \\' \
                               '   -cpu cortex-a72 \\' \
                               '   -nographic'
            elif 'x86_64' in image:
                arch = 'x86_64'
                console = 'console=ttyS0,115200n8'
                arch_options = '   -display none \\' \
                               '   -serial stdio'
            else:
                raise InvalidImageError(
                    f'Unknown architecture of image {image}!')

        if not kernel_commandline:
            kernel_commandline = f'root=/dev/vda1 rw {console}'

        image = os.path.abspath(image)
        image_dir = os.path.dirname(image)
        kernel = os.path.join(image_dir, 'vmlinuz')
        initrd = os.path.join(image_dir, 'initrd.img')
        image_format = image.split('.')[-1]

        memory = f'-m {memory}'

        qemu_cmd = f'qemu-system-{arch} \\' \
            f'   -m {memory} \\' \
            f'   -kernel {kernel} \\' \
            f'   -initrd {initrd} \\' \
            f'  -append "{kernel_commandline}" \\' \
            f' - drive file={image},format={image_format},if=virtio \\' \
            '   -device virtio-net-pci,netdev=eth0 \\' \
            '   -netdev user,id=eth0,ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,' \
            'ipv6-dns=fd00::eb:3 \\'

        qemu_cmd += arch_options

        logging.info('Running QEMU command:\n%s', qemu_cmd)

        self.send_keys(qemu_cmd)
