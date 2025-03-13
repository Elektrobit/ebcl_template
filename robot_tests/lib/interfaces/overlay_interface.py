"""
Image build abstractions.
"""
from abc import ABC, abstractmethod

from typing import Optional


class OverlayInterface(ABC):
    """
    Base class for all image interfaces.
    """

    @abstractmethod
    def build(self, path: str, build_target: str, result_file: str,  build_cmd: Optional[str]) -> Optional[str]:
        """
        Build all parts of the image.
        """

    @abstractmethod
    def clear(self, path: str, clear_cmd: Optional[str] = None) -> None:
        """
        Delete the build artifacts.
        """
