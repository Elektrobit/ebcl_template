# pylint: disable=invalid-name
"""
Generic helper functions.
"""
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
