""" EBcL initrd generator """
__version__ = "0.0.1"

from .initrd import main


def cli() -> None:
    """ Initrd package commandline interface entry point. """
    main()
