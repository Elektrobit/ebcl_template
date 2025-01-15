# pylint: disable=invalid-name
"""
Abstraction layer for image communication.
"""
import logging
import re
import time

from subprocess import Popen
from typing import Optional
from uuid import uuid4

from util.proc_io import ProcIO # type: ignore[import-untyped]


class TimeoutException(Exception):
    """ Command timeout. """


class LoginFailedException(Exception):
    """ Login to VM failed. """


class Comm:
    """
    Comm provides generic functions for communicating with running EBcL images.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

        self.io = None

    def __del__(self):
        if self.io:
            self.io.disconnect()

    def connect(self, process: Popen):
        """
        Connect to process.
        """
        logging.basicConfig(level=logging.DEBUG)
        self.io = ProcIO(process)
        self.io.connect()

    def disconnect(self):
        """
        Stop process.
        """
        self.io.disconnect()


    def send_message(self, message: str):
        """
        Send a message over the interface

        Appends a newline to the end iff none is present
        """
        logging.info('Send message %s...', message)

        if not message.endswith('\n'):
            message += '\n'

        self.io.write(message)

    def send_key(self, key: str):
        """
        Send a keystroke over the interface
        """
        logging.info('Send key %s...', key)

        self.io.write(key)

    def wait_for_line(self, search: str, timeout: int = -1) -> str:
        """
        Wait for a line containing the given search term.
        """
        logging.info('Waiting for line containing %s...', search)

        buf = ""
        start_time = time.time()
        while True:
            if timeout > 0 and time.time() - start_time >= timeout:
                logging.info('Timeout while waiting for term %s.\n%s', search, buf)
                raise TimeoutException()

            line = self.io.read_line(timeout=timeout)
            if not line:
                continue

            buf += line

            if search in line:
                logging.info('Matching line found: %s', line)
                return buf

    def wait_for_regex(self, regex: str, timeout: int = -1) -> re.Match:
        """
        Wait for a line matching the regex.

        Does NOT ignore leading and trailing whitespace,
        the regex needs to match the trailing newline
        """
        rg = re.compile(regex)
        logging.info('Waiting for regex %s...', rg)

        buf = ""
        start_time = time.time()
        while True:
            if timeout > 0 and time.time() - start_time >= timeout:
                logging.info('Timeout while waiting for regex %s.\n%s', regex, buf)
                raise TimeoutException()

            line = self.io.read_line(timeout=timeout)
            if not line:
                logging.info('No line during timeout.')
                continue

            buf += line

            m = rg.match(line)
            if m:
                logging.info('Match: %s\nFor line: %s', str(m), line)
                return m

    def execute(self, message, timeout: int = -1) -> str:
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
        self.io.write(f'{message}; echo {ter}\n')

        line = self.wait_for_line(ter, timeout=timeout)
        if f'echo {ter}' in line:
            logging.info('Skipping command echo: %s', line)
            line = self.wait_for_line(ter, timeout=timeout)

        logging.info('Command result: %s', line)

        return line

    def read_line(self, timeout: int = -1) -> Optional[str]:
        """ Read the next line. """
        return self.io.read_line(timeout)

    def clear_lines(self):
        """
        Clear all the output lines.
        """
        self.io.clear_lines()

    def login_to_vm(self, user: str = 'root', password: str = 'linux',
                    shell_prompt: str = '.*#.*', timeout: int = 30):
        """ Login to VM. """

        logging.info("Waiting for login prompt...")
        time.sleep(0.2)  # Give other processes and thread some time do work

        self.clear_lines()  # Delete all the output before trying to login

        self.send_key('\n')  # Press return to show the login prompt

        success = False
        line = None
        try:
            line = self.wait_for_line("login:", timeout=timeout)
            success = True
        except TimeoutException:
            logging.info("Trying to get login prompt by pressing enter...")
            for i in range(0, 30):
                logging.info('Try %d to get login prompt...', i)
                self.send_key('\n')
                try:
                    line = self.wait_for_line("login:", timeout=3)
                    success = True
                except TimeoutException:
                    continue

        if success:
            logging.info('Login prompt detected: %s', line)
        else:
            raise LoginFailedException()

        logging.info("Logging in with default credentials...")
        self.send_message(user)

        time.sleep(3)  # Give some time to process user

        self.send_message(password)

        logging.info("Trying to get shell prompt...")

        time.sleep(3)  # Give some time to process password

        success = False
        for i in range(0, 30):
            logging.info('Try %d to get shell prompt...', i)
            self.send_key('\n')
            try:
                m = self.wait_for_regex(shell_prompt, timeout=1)
                success = True
            except TimeoutException:
                continue
            if success:
                logging.info('Match for shell prompt: %s', str(m))
                logging.info('Login was successful.')
                return

        raise LoginFailedException()
