""" Tests for config helpers. """
import os

from ebcl.common.config import load_yaml


class TestApt:
    """ Tests for config helpers. """

    yaml_dir: str
    base: str
    derived: str

    @classmethod
    def setup_class(cls):
        """ Generate yaml path. """
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.yaml_dir = os.path.join(test_dir, 'data')
        cls.base = os.path.join(test_dir, 'data', 'base.yaml')
        cls.derived = os.path.join(test_dir, 'data', 'derived.yaml')

    def test_load_config_base(self):
        """ Test for loading a derived config. """
        config = load_yaml(self.base)
        assert 'a' in config and config['a'] == 'hello'
        assert 'b' in config and config['b'] == 123
        assert 'c' in config and config['c'] == ['a', 'b', 'c']
        assert 'd' in config and config['d'] == {'e': 'f', 'j': 'k'}
        assert 'l' in config and config['l'] == [{'s': 't', 'i': 'j'}]

    def test_load_config_derived(self):
        """ Test for loading a derived config. """
        config = load_yaml(self.derived)
        assert 'a' in config and config['a'] == 'hello'
        assert 'b' in config and config['b'] == 456
        assert 'c' in config and config['c'] == ['x', 'y', 'a', 'b', 'c']
        assert 'd' in config and config['d'] == {'e': 'z', 'j': 'k', 'u': 'v'}
        assert 'l' in config and config['l'] == [
            {'h': 'j', 'k': 'l'}, {'s': 't', 'i': 'j'}]

    def test_more_base(self):
        """ Test for loading a derived config. """
        yaml = os.path.join(self.yaml_dir, 'derived2.yaml')
        config = load_yaml(yaml)
        assert 'a' in config and config['a'] == 'hello'
        assert 'b' in config and config['b'] == 456
        assert 'c' in config and config['c'] == ['x', 'y', 'a', 'b', 'c']
        assert 'd' in config and config['d'] == {'e': 'z', 'j': 'k', 'u': 'v'}
        assert 'l' in config and config['l'] == [
            {'h': 'j', 'k': 'l'}, {'s': 't', 'i': 'j'}]
        assert 'a' in config and config['z'] == 'other'
