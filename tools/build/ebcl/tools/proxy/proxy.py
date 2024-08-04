#!/usr/bin/env python
""" EBcL apt proxy commandline interface. """
import argparse
import logging

from ebcl.common import init_logging

# TODO: implmement


def main() -> None:
    """ Main entrypoint of EBcL apt proxy. """
    init_logging()

    parser = argparse.ArgumentParser(
        description='EBcL apt proxy.')

    _args = parser.parse_args()

    logging.critical('Not implemented!')


if __name__ == '__main__':
    main()
