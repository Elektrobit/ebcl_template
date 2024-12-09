"""
Taskfile implementation of the image interface.
"""
import logging
import os

from typing import Optional

from Fakeroot import Fakeroot
from interfaces.image_interface import ImageInterface


class TaskBuild(ImageInterface):
    """
    Taskfile implementation of the image interface.
    """

    def __init__(self):
        self.fake = Fakeroot()

    def build(self, path: str, build_cmd: Optional[str] = None) -> Optional[str]:
        """
        Build all parts of the image.
        """
        if build_cmd is None:
            build_cmd = 'task build'

        self.fake.run(build_cmd, cwd=path, stderr_as_info=True)

        image = os.path.join(path, 'build', 'image.raw')

        if os.path.isfile(image):
            return image
        else:
            return None


    def clear(self, path: str) -> None:
        """
        Delete the build artifacts.
        """
        if os.path.isfile(os.path.join(path, 'build', 'image.raw')):
            skip = os.getenv('SDK_ROBOT_SKIP_CLEAN', '0')
            if skip == '1':
                logging.info('SDK_ROBOT_SKIP_CLEAN is 1, skipping image rebuild.')
                return

        self.fake.run('task gen:clean', cwd=path, stderr_as_info=True)
