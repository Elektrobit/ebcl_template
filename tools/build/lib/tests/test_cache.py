""" Tests for the cache functions. """
import os
import shutil
import tempfile

from pathlib import Path

from ebcl.cache import Cache


class TestCache:
    """ Tests for the cache functions. """

    folder: Path
    cache: Cache

    @classmethod
    def setup_class(cls):
        """ Prepare cache object. """
        cls.folder = Path(tempfile.mkdtemp()).absolute()
        cls.cache = Cache(folder=cls.folder.name)

    @classmethod
    def teardown_class(cls):
        """ Delete cache folder. """
        shutil.rmtree(cls.folder)
        assert False

    def test_add(self):
        """ Add a pacakage. """
        self.cache.add('amd64', 'busybox', '1:1.35.0-4', '/my/path/to/deb')

        p = self.cache.get('amd64', 'busybox', '1:1.35.0-4')
        assert p == '/my/path/to/deb'

        p = self.cache.get('amd64', 'busybox', 'anotherversion')
        assert p is None

    def test_get_no_version(self):
        """ Get any version of a package. """
        self.cache.add('amd64', 'busybox', '1:1.35.0-4', '/my/path/to/deb')

        p = self.cache.get('amd64', 'busybox')
        assert p == '/my/path/to/deb'

    def test_cache_miss(self):
        """ Package does not exist. """
        p = self.cache.get('amd64', 'not-existing')
        assert p is None

        p = self.cache.get('nonearch', 'not-existing')
        assert p is None

        p = self.cache.get('amd64', 'busybox', 'nonversion')
        assert p is None
