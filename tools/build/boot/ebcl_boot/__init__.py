""" EBcL boot generator """
__version__ = "0.0.1"

from .boot import main


def cli() -> None:
    """ Boot package commandline interface entry point. """
    main()
