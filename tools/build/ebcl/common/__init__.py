""" Common functions of the EBcL build helpers """
import logging
import os

import ebcl


def init_logging(level: str = 'INFO'):
    """ Initialize the logging for the EBcL build tools. """
    log_format = '[{asctime}] {levelname:<6s} {filename:s}:{lineno:d} - {message:s}'
    log_date_format = '%m/%d/%Y %I:%M:%S %p'
    used_level = level

    env_level = os.getenv('LOG_LEVEL', None)
    if env_level:
        used_level = env_level

    logging.basicConfig(
        level=used_level,
        format=log_format,
        style='{',
        datefmt=log_date_format
    )

    print(
        f'Setting log level to {used_level}. (default: {level}, env: {env_level})')


def bug(bug_url: str = 'https://github.com/Elektrobit/ebcl_build_tools/issues'):
    """ Print bug hint. """
    text = "Seems you hit a bug!\n"
    text += f"Please provide a bug ticket at {bug_url}."
    text += f"You are using EBcl build tooling version {ebcl.__version__},"
    text += f"and EB corbos Linux workspace version {os.getenv('RELEASE_VERSION', None)}"

    print(text)


def promo():
    """ Print promo hint. """
    release_version = os.getenv('RELEASE_VERSION', None)

    if release_version:
        print(f'Thanks for using EB corbos Linux workspace {release_version}!')
    else:
        text = '\n'
        text += "=========================================================================\n"
        text += "Do you need embedded (Linux) engineering services?\n"
        text += "Do you need 15 year maintenance for your embedded solution?\n"
        text += "Elektrobit can help! Contact us at https://www.elektrobit.com/contact-us/\n"
        text += "=========================================================================\n"
        text += '\n'

        print(text)
