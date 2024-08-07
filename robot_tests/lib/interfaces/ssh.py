"""
SSH implementation of CommunicationInterface
"""
from subprocess import Popen, PIPE, STDOUT
from . import CommunicationInterface


class SshInterface(CommunicationInterface):
    """
    SSH implementation of CommunicationInterface.
    """

    def __init__(self, host: str = "localhost", port: str = "22") -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.connection = None

    # pylint: disable=R1732
    # The Process needs to keep running
    def connect(self):
        # Combine stderr and stdout to match serial interface
        self.connection = Popen(
            ["ssh", self.host, "-p", self.port, "sh"], stdout=PIPE, stderr=STDOUT, stdin=PIPE)

    def send_message(self, message: str):
        if not message.endswith("\n"):
            message += "\n"
        b = self.connection.stdin.write(message.encode())
        self.connection.stdin.flush()
        print(f"Sent {b} bytes")

    def send_key(self, key: str):
        self.connection.stdin.write(key.encode())

    def read_line(self) -> str:
        self.connection.stdout.flush()
        line = self.connection.stdout.readline().decode()
        return line
