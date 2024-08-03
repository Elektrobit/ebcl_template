""" Debian package dependency resolution. """
import logging

from typing import Any, Optional

from ebcl.common.deb import Package
from ebcl.common.proxy import Proxy
from ebcl.common.version import VersionDepends


def vds_to_packages(
        vds: list[VersionDepends], proxy: Proxy
) -> Optional[list[Package]]:
    """ Use proxy to find all the given VersionDepends. """
    packages = []

    for vd in vds:
        p = proxy.find_package(vd)
        if not p:
            logging.error('Package %s not found!', vd)
            return None

        packages.append(p)

    return packages


def _contains_package(
        packages: list[Package], vd: VersionDepends
) -> bool:
    """ Tests if the given package is contained. """
    return True


def check_package_set(package_set: list[Package]) -> bool:
    """ Check if the given  """
    forbidden = []

    for p in package_set:
        for fbs in p.breaks:
            for fb in fbs:
                pass

    return False


class WordGenerator:
    """ Generates all words for the given letters. """

    letters: list[list[Any]]
    variants: list[int]
    current: list[int]
    pointer: int
    word_len: int

    def __init__(self, letters: list[list[Any]]):
        """ Set letters to use. """
        self.letters = letters
        self.word_len = len(letters)

        self.current = [0] * self.word_len

        self.pointer = -2

        self.variants = []
        for a in letters:
            self.variants.append((len(a) - 1))

    def _next_int_word(self) -> bool:
        """ Generate the indices for the next word. """
        if self.pointer == -2:
            # first word
            self.pointer = -1
            return True

        # Check if there is a next word
        next_word = False
        for i, v in enumerate(self.variants):
            if self.current[i] < v:
                next_word = True
                break

        if not next_word:
            return False

        wl = self.word_len
        ptr = self.pointer

        # Shift the '1' to the next available position
        # Find the next available position
        next_pos = -1
        for i in range(ptr + 1, wl):
            # Wrap around
            if self.current[i] < self.variants[i]:
                next_pos = i
                break

        if next_pos >= 0:
            if ptr >= 0:
                # Remove the '1'
                self.current[ptr] -= 1
        else:
            next_pos = 0

        # Add the '1'
        self.current[next_pos] += 1

        # Shift the pointer
        self.pointer = next_pos

        return True

    def next_word(self) -> Optional[list[Any]]:
        """ Get the next word. """
        has_next = self._next_int_word()
        if not has_next:
            return None

        word = []

        for i, l in enumerate(self.current):
            word.append(self.letters[i][l])

        return word
