""" Unit tests for the EBcL initrd generator. """
import os
from ebcl_initrd.initrd import InitrdGenerator


class TestInitrd:
    """ Unit tests for the EBcL initrd generator. """

    yaml: str

    @classmethod
    def setup_class(cls):
        """ Prepare apt repo object. """
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.yaml = os.path.join(test_dir, 'data', 'initrd.yaml')

    def test_read_config(self):
        """ Test yaml config loading. """
        generator = InitrdGenerator(self.yaml)
        assert generator.arch == 'arm64'
        assert generator.root_device == '/dev/mmcblk0p2'
