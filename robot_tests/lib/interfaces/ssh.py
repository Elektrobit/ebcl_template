"""
SSH implementation of CommunicationInterface
"""
from .process import ShellSubprocess


class SshInterface(ShellSubprocess):
    """
    SSH implementation of CommunicationInterface.
    """

    def __init__(self, host: str = "localhost", port: str = "22") -> None:
        super().__init__()
        self.host = host
        self.port = port

    def _process_command(self) -> list[str]:
        """ Get the command to execute. """
        return ["ssh", self.host, "-p", self.port, "sh"]
