# pylint: disable=invalid-name
"""
Abstraction layer for image building.
"""
import logging
import os

from typing import Optional

from interfaces.image_task import TaskBuild # type: ignore[import-untyped]
from interfaces.image_download import DirectDownload

class NoImage(Exception):
    """ Raised if no image was specified. """


class Image:
    """
    Image provides generic functions for building EBcL images.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

        self.mode = os.getenv('EBCL_TF_BUILD_MODE', 'Taskfile')
        self.image_base = os.getenv('EBCL_TF_IMAGE_BASE', '/workspace/images/')

        logging.info('Setting up Image with interface %s and image base path %s...', self.mode, self.image_base)

        match self.mode:
            case 'Taskfile':
                self.interface = TaskBuild()
            case 'Download':
                self.interface = DirectDownload()
            case x:
                raise ValueError(
                    f"Unknown communication interface '{x}' specified")


    def build(self, path: Optional[str] = None, build_cmd: Optional[str] = None) -> Optional[str]:
        """
        Build all parts of the image.
        """
        if path is None or path == '':
            path = os.environ['EBCL_TC_IMAGE']

        if path is None or path == '':
            raise NoImage()

        image_path = os.path.join(self.image_base, path)

        build_cmd = os.getenv('EBCL_TF_BUILD_CMD', build_cmd)

        logging.info('Using image path %s and build command %s...', image_path, build_cmd)

        return self.interface.build(image_path, build_cmd)

    def clear(self, path: str, clear_cmd: Optional[str] = None):
        """
        Delete the build artifacts.
        """
        if path is None or path == '':
            path = os.environ['EBCL_TC_IMAGE']

        if path is None or path == '':
            raise NoImage()

        image_path = os.path.join(self.image_base, path)

        clear_cmd = os.getenv('EBCL_TF_CLEAR_CMD', clear_cmd)

        logging.info('Using image path %s clear command %s...', image_path, clear_cmd)

        self.interface.clear(image_path, clear_cmd)
