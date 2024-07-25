""" Deb helper funktions. """
import shutil
import tarfile
import tempfile

from pathlib import Path

import unix_ar
import zstandard


def extract_archive(deb_file: str, location: str | None = None) -> str:
    """ Extract a deb archive. """
    if location is None:
        location = tempfile.mkdtemp()

    deb_content_location = tempfile.mkdtemp()

    # extract deb
    file = unix_ar.open(deb_file)
    file.extractall(deb_content_location)

    # find data.tar
    tar_file = Path(deb_content_location).glob('data.tar.*').__next__()
    assert tar_file is not None

    # decompress zstd file
    if tar_file.name.endswith('.zst'):
        with open(tar_file, 'rb') as compressed:
            decomp = zstandard.ZstdDecompressor()
            output_path = Path(location) / 'data.tar'
            with open(output_path, 'wb') as destination:
                decomp.copy_stream(compressed, destination)
        tar_file = output_path

    # extract data.tar
    tar = tarfile.open(tar_file.absolute())
    data = Path(location)
    tar.extractall(path=data)
    tar.close()

    shutil.rmtree(deb_content_location)

    return location
