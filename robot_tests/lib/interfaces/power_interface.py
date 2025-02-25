"""
Power state abstractions.
"""
from abc import ABC, abstractmethod

from typing import Any, Optional


class PowerInterface(ABC):
    """
    Base class for all image interfaces.
    """

    @abstractmethod
    def power_on(
        self,
        image: Optional[str],
        cmd: Optional[str] = None,
        env: dict[str, str] = []
    ) -> Any:
        """
        Run the image.
        """

    @abstractmethod
    def power_off(self, cmd: Optional[str] = None):
        """
        Stop the image by "power-cut".
        """
