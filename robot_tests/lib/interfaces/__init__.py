"""
This module contains the base class for all CommunicationInterfaces
as well as the concrete implementations.
"""
from abc import ABC, abstractmethod
from typing import Optional


class CommunicationInterface(ABC):
    """
    Base class for all communication interfaces.

    All communication should only occur over methods defined in this class
    """

    def __init__(self) -> None:
        self.lines = ""

    @abstractmethod
    def connect(self):
        """
        Perform any actions needed to establish the actual connection to the target
        """

    @abstractmethod
    def disconnect(self):
        """
        Perform any actions needed to stop the actual connection to the target
        """

    @abstractmethod
    def send_message(self, message: str):
        """
        Send a message over the interface

        Override this for your implementation

        Implementation should append a line break iff it is not present
        """

    @abstractmethod
    def send_key(self, key: str):
        """
        Send a single keystroke over the interface

        Override this for your implementation
        """

    def send_keys(self, keys: str):
        """
        Send multiple keys over the interface. 

        This may or may not be
        semantically different from sending a message with `send_message`

        Do NOT override
        """
        for key in keys:
            self.send_key(key)

    @abstractmethod
    def read_line(self, timeout: int = 1) -> Optional[str]:
        """
        Read one line (including the line break) from the interface

        Override this for your implementation
        """

    def next_line(self, timeout: int = 1) -> Optional[str]:
        """
        Read one line (including the line break) from the interface
        and append it to the internal log.

        Do NOT override
        """
        line = self.read_line(timeout=timeout)
        if line:
            self.lines += line
        return line

    @abstractmethod
    def clear_lines(self):
        """
        Clear all the output lines.
        """
