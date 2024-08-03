""" Tests for the Debian package dependency resolution. """
import logging

from ebcl.common.dependency import WordGenerator


class TestWordGenerator:

    def test_no_alternatives(self):
        """ Test the case that there are no alternatives. """
        letters = [['a'], ['b'], ['c'], ['d'], ['e']]

        generator = WordGenerator(letters)

        next_word = generator.next_word()
        assert next_word == ['a', 'b', 'c', 'd', 'e']

        next_word = generator.next_word()
        assert next_word is None

    def test_alternatives(self):
        """ Test the case that there are no alternatives. """
        letters = [
            ['a', 'u', 'v'],
            ['b', 'l'],
            ['c'],
            ['d', 'm', 'n', 'o'],
            ['e']
        ]

        words = [
            ['a', 'b', 'c', 'd', 'e'],
            ['u', 'b', 'c', 'd', 'e'],
            ['a', 'l', 'c', 'd', 'e'],

            ['a', 'b', 'c', 'm', 'e'],
            ['u', 'b', 'c', 'm', 'e'],
            ['a', 'l', 'c', 'm', 'e'],

            ['a', 'b', 'c', 'n', 'e'],
            ['u', 'b', 'c', 'n', 'e'],
            ['a', 'l', 'c', 'n', 'e'],

            ['a', 'b', 'c', 'o', 'e'],
            ['u', 'b', 'c', 'o', 'e'],
            ['a', 'l', 'c', 'o', 'e'],

            ['u', 'l', 'c', 'o', 'e'],
            ['v', 'l', 'c', 'o', 'e'],
        ]

        generator = WordGenerator(letters)

        for i, w in enumerate(words):
            next_word = generator.next_word()
            logging.info('Testing word %d: %s == %s', i, w, next_word)
            assert w == next_word

        next_word = generator.next_word()
        assert next_word is None
