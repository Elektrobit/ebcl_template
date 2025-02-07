"""
Taskfile implementation of the image interface.
"""
import logging
import os
import requests

from typing import Optional

from Fakeroot import Fakeroot
from interfaces.image_interface import ImageInterface
from Util import Util
import tarfile


class DirectDownload(ImageInterface):
    """
    Taskfile implementation of the image interface.
    """

    def __init__(self):
        self.fake = Fakeroot()

    def build(self, path: str, build_cmd: Optional[str] = None) -> Optional[str]:
        """
        Download the image from the specified URL and save it to the output directory.
        """
        image_url, arti_user, arti_token = self._get_credentials()
        if not image_url or not arti_user or not arti_token:
            return None

        session = requests.Session()
        session.auth = (arti_user, arti_token)

        if not os.path.exists(path):
            os.makedirs(path)

        return self._download_and_extract_image(session, image_url, path)

    def clear(self, path: str, clear_cmd: Optional[str] = None) -> None:
        """
        Delete the downloaded files.
        """

        if os.path.exists(path):
            skip = os.getenv('SDK_ROBOT_SKIP_CLEAN', '0')
            if skip == '1':
                logging.warning('SDK_ROBOT_SKIP_CLEAN is 1, skipping image rebuild.')
                return

            os.remove(path)

    def _get_credentials(self) -> tuple:
        image_url = Util().get_env('EBCL_IMAGE_BUNDLE_URL', '')
        arti_user = Util().get_env('ARTIFACTORY_USER', '')
        arti_token = Util().get_env('ARTIFACTORY_IDENTITY_TOKEN', '')
        arti_token_file = Util().get_env('ARTIFACTORY_IDENTITY_TOKEN_FILE', '')

        if not arti_user or not arti_token:
            try:
                with open(arti_token_file, 'r') as file:
                    lines = file.readlines()
                    if len(lines) > 2:
                        arti_user = lines[1].split(' ', 1)[1].strip()
                        arti_token = lines[2].split(' ', 1)[1].strip()
                    else:
                        logging.error("Credentials file does not contain enough lines.")
                        return '', '', ''
            except FileNotFoundError:
                logging.error("Credentials file not found and environment variables are not set.")
                return '', '', ''

        return image_url, arti_user, arti_token

    def _download_and_extract_image(self, session, image_url: str, path: str) -> Optional[str]:
        response = session.get(image_url)
        if response.ok:
            bundle_filename = os.path.basename(image_url)
            bundle_path = os.path.join(path, bundle_filename)
            try:
                with open(bundle_path, 'wb') as file:
                    file.write(response.content)

                    # Decompress the tarball
                    if tarfile.is_tarfile(bundle_path):
                        with tarfile.open(bundle_path, 'r:*') as tar:
                            tar.extractall(path=path)
                        os.remove(bundle_path)
                    else:
                        logging.error(f"The downloaded file {bundle_filename} is not a valid tarball.")
                        return None
            except (OSError, tarfile.TarError) as e:
                logging.error(f"An error occurred while handling the file: {e}")
                return None

            for root, dirs, files in os.walk(path):
                for file in files:
                    if 'image' in file:
                        return os.path.join(root, file)

            logging.error("No file containing 'image' found in the specified path.")
            return None
        else:
            logging.error(f"Failed to download image from {image_url} with error code: {response.status_code}")
            return None
