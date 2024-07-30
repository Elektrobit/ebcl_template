""" Unit tests for the version helpers. """
from ebcl.version import Version


class TestVersion:
    """ Unit tests for the version helpers. """

    def _to_versions(self, texts: list[str]) -> list[Version]:
        """ Convert strings to versions. """
        return [Version(t) for t in texts]

    def test_version_parsing(self):
        """ Tests parsing of deb versions. """
        v = Version('2.0.12-1ubuntu1')
        assert v.epoch == 0
        assert v.version == '2.0.12'
        assert v.revision == '1ubuntu1'

        v = Version('2.0.12-1-1ubuntu1')
        assert v.epoch == 0
        assert v.version == '2.0.12-1'
        assert v.revision == '1ubuntu1'

        v = Version('1:2.0.12-1-1ubuntu1')
        assert v.epoch == 1
        assert v.version == '2.0.12-1'
        assert v.revision == '1ubuntu1'

    def test_version_compare(self):
        """ Tests version sorting. """
        versions = self._to_versions([
            '6.8.0-39.39',
            '6.8.0-31.31',
            '6.8.0-35.31'
        ])

        versions.sort()

        assert versions[0] == Version('6.8.0-31.31')
        assert versions[-1] == Version('6.8.0-39.39')

        versions = self._to_versions([
            '8.0.8-0ubuntu1~24.04.1',
            '8.0.8-0ubuntu1~24.04.2',
            '8.0.7-0ubuntu1~24.04.1'
        ])
        versions.sort()

        assert versions[0] == Version('8.0.7-0ubuntu1~24.04.1')
        assert versions[-1] == Version('8.0.8-0ubuntu1~24.04.2')

        versions = self._to_versions([
            '2.42.10+dfsg-3ubuntu3.1',
            '2.42.10+ffsg-3ubuntu3.1',
            '2.42.10+afsg-3ubuntu3.1',
            '2.42.10+ffsg-3ubuntu3'
        ])
        versions.sort()

        assert versions[0] == Version('2.42.10+afsg-3ubuntu3.1')
        assert versions[1] == Version('2.42.10+dfsg-3ubuntu3.1')
        assert versions[2] == Version('2.42.10+ffsg-3ubuntu3')
        assert versions[3] == Version('2.42.10+ffsg-3ubuntu3.1')

    def test_partial_version(self):
        """ Test comparison of partial version string. """
        vp = Version('1.66ubuntu1')
        vd = Version('1.66~')
        assert vd < vp
