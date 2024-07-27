""" Tests for the cache functions. """
import shutil
import tempfile

from ebcl.cache import Cache


class TestCache:
    """ Tests for the cache functions. """

    folder: str
    cache: Cache

    @classmethod
    def setup_class(cls):
        """ Prepare cache object. """
        cls.folder = tempfile.mkdtemp()
        cls.cache = Cache(folder=cls.folder)

    @classmethod
    def teardown_class(cls):
        """ Delete cache folder. """
        shutil.rmtree(cls.folder)

    def test_add(self):
        """ Add a pacakage. """
        res = self.cache.add(
            '/my/path/to/busybox-static_1.30.1-7ubuntu3_amd64.deb')
        assert res

        p = self.cache.get('amd64', 'busybox-static', '1.30.1-7ubuntu3')
        assert p == '/my/path/to/busybox-static_1.30.1-7ubuntu3_amd64.deb'

        p = self.cache.get('amd64', 'busybox-static', 'anotherversion')
        assert p is None

    def test_invalid_name(self):
        """ Test that invalid name is not added. """
        res = self.cache.add(
            '/my/path/to/busybox-static_1.30.1-7ubuntu3_amd64.dsc')
        assert not res

        res = self.cache.add(
            '/my/path/to/busybox-static_1.30.1-7ubuntu3-amd64.deb')
        assert not res

    def test_get_no_version(self):
        """ Get any version of a package. """
        res = self.cache.add(
            '/my/path/to/busybox-static_1.30.1-7ubuntu3_amd64.deb')
        assert res

        p = self.cache.get('amd64', 'busybox-static')
        assert p == '/my/path/to/busybox-static_1.30.1-7ubuntu3_amd64.deb'

    def test_cache_miss(self):
        """ Package does not exist. """
        p = self.cache.get('amd64', 'not-existing')
        assert p is None

        p = self.cache.get('nonearch', 'not-existing')
        assert p is None

        p = self.cache.get('amd64', 'busybox', 'nonversion')
        assert p is None

    def test_restore_cache(self):
        """ Test for restoring cache index. """
        cache = Cache()
        res = cache.add('/my/path/to/busybox_1.30.1-7ubuntu3_amd64.deb')
        assert res

        cache.save()

        del cache

        cache = Cache()
        p = cache.get('amd64', 'busybox')
        assert p == '/my/path/to/busybox_1.30.1-7ubuntu3_amd64.deb'
