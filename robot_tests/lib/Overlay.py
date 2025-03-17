# pylint: disable=invalid-name
"""
Abstraction layer for handling test overlays.

The implementation assumes that the image mounts a test overlay provided as kernel commandline
test_overlay parameter before the image manager is execute on top of the root filesystem.
"""
import logging
import os

from typing import Optional

from interfaces.overlay_task import TaskBuild # type: ignore[import-untyped]
from interfaces.overlay_download import DirectDownload

class NoImage(Exception):
    """ Raised if no image was specified. """


class Overlay:
    """
    Image provides generic functions for building EBcL images overlays.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

        self.mode = os.getenv('EBCL_TF_BUILD_MODE', 'Taskfile')
        self.overlay_base = os.getenv('EBCL_TF_TEST_OVERLAY_FOLDER', '/workspace/images/test_extensions')

        logging.info('Setting up Image with interface %s and image base path %s...', self.mode, self.overlay_base)

        match self.mode:
            case 'Taskfile':
                self.interface = TaskBuild()
            case 'Download':
                self.interface = DirectDownload()
            case x:
                raise ValueError(
                    f"Unknown communication interface '{x}' specified")


    def build_overlay(self, build_target: str, result_file: str, path: Optional[str] = None, build_cmd: Optional[str] = None) -> Optional[str]:
        """
        Build all parts of the image.
        """
        if path is None:
            path = ''

        test_overlay_path = os.path.join(self.overlay_base, path)

        build_cmd = os.getenv('EBCL_TF_OVERLAY_BUILD_CMD', build_cmd)

        logging.info('Using test overlay path %s and build command %s...', test_overlay_path, build_cmd)

        return self.interface.build(test_overlay_path, build_target, result_file, build_cmd)

    def clear_overlay(self, path: str, clear_cmd: Optional[str] = None):
        """
        Delete the build artifacts.
        """
        if path is None:
            path = ''

        test_overlay_path = os.path.join(self.overlay_base, path)

        clear_cmd = os.getenv('EBCL_TF_OVERLAY_CLEAR_CMD', clear_cmd)

        logging.info('Using test overlay path %s clear command %s...', test_overlay_path, clear_cmd)

        self.interface.clear(test_overlay_path, clear_cmd)
