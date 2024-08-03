""" Tests for the cache functions. """
import shutil
import tempfile

from ebcl.common.cache import Cache
from ebcl.common.deb import Package
from ebcl.common.version import Version, VersionRealtion


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
        res = self.cache.add(Package.from_deb(
            '/workspace/tools/build/tests/data/busybox-static_1.36.1-3ubuntu1_amd64.deb', []))
        assert res

        v = Version('1.36.1-3ubuntu1')
        p = self.cache.get('amd64', 'busybox-static', v,
                           relation=VersionRealtion.EXACT)
        assert p
        assert p.name == 'busybox-static'
        assert p.arch == 'amd64'
        assert p.version == v

        p = self.cache.get('amd64', 'busybox-static',
                           Version('anotherversion'), VersionRealtion.EXACT)
        assert not p

    def test_get_no_version(self):
        """ Get any version of a package. """
        res = self.cache.add(Package.from_deb(
            '/workspace/tools/build/tests/data/busybox-static_1.36.1-3ubuntu1_amd64.deb', []))
        assert res

        p = self.cache.get('amd64', 'busybox-static')
        assert p
        assert p.name == 'busybox-static'
        assert p.arch == 'amd64'
        assert p.version == Version('1.36.1-3ubuntu1')

    def test_cache_miss(self):
        """ Package does not exist. """
        p = self.cache.get('amd64', 'not-existing')
        assert p is None

        p = self.cache.get('nonearch', 'not-existing')
        assert p is None

        p = self.cache.get('amd64', 'busybox', Version('nonversion'),
                           VersionRealtion.EXACT)
        assert p is None

    def test_restore_cache(self):
        """ Test for restoring cache index. """
        cache = Cache()
        res = cache.add(Package.from_deb(
            '/workspace/tools/build/tests/data/busybox-static_1.36.1-3ubuntu1_amd64.deb', []))
        assert res

        del cache

        cache = Cache()
        p = cache.get('amd64', 'busybox-static', Version('1.36.1-3ubuntu1'))
        assert p
        assert p.name == 'busybox-static'
        assert p.arch == 'amd64'
        assert p.version == Version('1.36.1-3ubuntu1')
