"""
Abstraction layer for image building.
"""
import logging
import os

from typing import Optional

from interfaces.image_task import TaskBuild


class Image:
    """
    Image provides generic functions for building EBcL images.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self, mode='Taskfile', image_base='/workspace/images/') -> None:
        logging.basicConfig(level=logging.DEBUG)

        logging.info('Setting up CommManager with interface %s...', mode)

        self.mode = mode
        self.image_base = image_base

        match mode:
            case 'Taskfile':
                self.interface = TaskBuild()
            case x:
                raise ValueError(
                    f"Unknown communication interface '{x}' specified")


    def build(self, path: str, build_cmd: Optional[str] = None) -> Optional[str]:
        """
        Build all parts of the image.
        """
        return self.interface.build(os.path.join(self.image_base, path), build_cmd)

    def clear(self, path: str):
        """
        Delete the build artifacts.
        """
        self.interface.clear(os.path.join(self.image_base, path))
