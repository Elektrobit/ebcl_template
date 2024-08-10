# pylint: disable=C0103
"""
Allows Robot to communicate with a physical or virtual target
while abstracting away the concrete communication channel
"""
import logging
import re
import time

from typing import Any, Optional
from uuid import uuid4

from interfaces.ssh import SshInterface
from interfaces.tmux import TmuxConsole
from interfaces.process import ShellSubprocess


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

            if ter in line:
                logging.info('Line %s matches terminator...', line)
                return buf

            buf += line

    def login_to_vm(self, user: str = 'root', password: str = 'linux',
                    shell_prompt: str = '.*#.*') -> bool:
        """ Login to VM. """
        logging.info("Waiting for login prompt...")

        time.sleep(1)  # Give other processes and thread some time do work
        self.clear_lines()  # Delete all the output bevor trying to login

        self.send_keys('\n')  # Press return to show the login prompt

        m = self.wait_for_regex(".*login:.*", timeout=30)
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
        time.sleep(1)
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
