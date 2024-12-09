"""
Image build abstractions.
"""
from abc import ABC, abstractmethod

from typing import Optional


class ImageInterface(ABC):
    """
    Base class for all image interfaces.
    """

    @abstractmethod
    def build(self, path: str, build_cmd: Optional[str]) -> Optional[str]:
        """
        Build all parts of the image.
        """

    @abstractmethod
    def clear(self, path: str) -> None:
        """
        Delete the build artifacts.
        """
