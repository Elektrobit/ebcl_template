# pylint: disable=C0103
"""
Allows Robot to communicate with a physical or virtual target
while abstracting away the concrete communication channel
"""
import os
import re
import socket
import time

from typing import Any
from uuid import uuid4

from interfaces.ssh import SshInterface
from interfaces.tmux import TmuxConsole


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
        self.mode = mode
        match mode:
            case "SSH":
                self.interface = SshInterface(*args)
            case "Serial":
                self.interface = TmuxConsole(*args)
            case x:
                raise ValueError(
                    f"Unknown communication interface '{x}' specified")

    def connect(self):
        """
        Perform any actions needed to establish the actual connection to the target
        """
        self.interface.connect()

    def send_message(self, message: str):
        """
        Send a message over the interface

        Appends a newline to the end iff none is present
        """

        self.interface.send_message(message)

    def send_key(self, key: str):
        """
        Send a keystroke over the interface
        """
        self.interface.send_key(key)

    def wait_for_line(self, line: str):
        """
        Ingest lines until a matching line is found
        Ignores leading and trailing whitespace
        """
        while True:
            r = self.interface.next_line()
            print(r)
            if line.strip() == r.strip():
                return

    def wait_for_line_exact(self, line: str):
        """
        Ingest lines until a matching line is found
        Does NOT ignores leading and trailing whitespace
        """
        while True:
            r = self.interface.next_line()
            print(r)
            if line == r:
                return

    def wait_for_regex(self, regex: str) -> re.Match:
        """
        Ingest lines until a line matching the regex is found.

        Does NOT ignore leading and trailing whitespace,
        the regex needs to match the trailing newline
        """
        rg = re.compile(regex)
        while True:
            line = self.interface.next_line()
            print(line)
            m = rg.match(line)
            if not m:
                continue
            return m

    def execute(self, message) -> str:
        """
        Read all lines produced by the given message
        """
        terminator = uuid4()
        ter = str(terminator)
        self.send_message(message + "; echo " + ter)
        buf = ""
        while True:
            r = self.interface.next_line()
            if r == ter:
                break
            buf += r
        return buf

    def test_setup(self, image: str, fmt: str, arch: str):
        """
        Check if qemu is running, if no, run it
        """
        script = os.path.join(os.path.dirname(__file__), 'run_qemu.sh')
        qcmd = f"{script} {image} {fmt} {arch} \n"

        hostname = socket.gethostname()
        output = self.execute("hostname")

        if hostname not in output:
            print("qemu is up and running")
        else:
            self.send_key(qcmd)
            self.wait_for_regex(".*login:.*")
            self.send_key("root\n")
            time.sleep(0.5)
            self.send_key("linux\n")

    def create_session(self, session_name: str):
        """
        Create new session and window in case of serial mode

        Args:
            session_name (str): session name
            window_name (str): window name
        """
        if self.mode == "Serial":
            self.interface.create_session(session_name)
