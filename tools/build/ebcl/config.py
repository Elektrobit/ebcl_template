""" Yaml loading helpers. """
import logging
import os

from typing import Any

import yaml


def _merge(base: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """ Merge the dicts. """
    for key, value in base.items():
        if key not in config:
            config[key] = value
            continue

        if isinstance(value, dict):
            # Recursion
            _merge(value, config[key])

        elif isinstance(value, list):
            config[key] += value

        elif isinstance(value, str):
            continue
        elif isinstance(value, int):
            continue

        else:
            logging.warning('Cannot merge value %s of type %s',
                            value, type(value))

    return config


def load_yaml(config_file: str) -> dict[str, Any]:
    """ Parse the yaml config file.

    Supports multi-level yamls. The key for the base yaml is 'base'

    Args:
        config_file (Path): Path to the yaml config file.
    """
    config: dict[str, Any] = {}

    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if 'base' in config:
        base_yaml = config['base']
        path = os.path.abspath(os.path.join(
            os.path.dirname(config_file), base_yaml))

        # Recursion
        base_config = load_yaml(path)

        if isinstance(base_config, dict):
            config = _merge(base_config, config)
        else:
            logging.critical(
                'Base config %s has no dict root! Config is ignored.', path)

    return config
