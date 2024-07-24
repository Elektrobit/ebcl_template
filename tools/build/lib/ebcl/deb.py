""" Deb helper funktions. """
import tempfile
import unix_ar


def extract_archive(deb_file: str, location: str | None) -> str:
    """ Extract a deb archive. """
    file = unix_ar.open(deb_file)
    if location is None:
        location = tempfile.mkdtemp()
    file.extractall(location)
    return location
