# pylint: disable=invalid-name
"""
Generic helper functions.
"""
import logging
import os


class Util:
    """
    Generic helper functions.
    """

    def filter_lines_containing(self, lines: str, search: str) -> str:
        """
        Remove all lines containing the search term.
        """
        lines.split('\n')
        filtered_lines = [line for line in lines if not search in line]
        return '\n'.join(filtered_lines)

    def set_env(self, variable: str, value: str) -> None:
        """
        Set a environment variable
        """
        os.environ[variable] = value
        
    def get_env(self, variable: str, default: str) -> str:
        """
        Get a environment variable
        """
        logging.info('Getting environment variable %s...', variable)
        return os.getenv(variable, default)
