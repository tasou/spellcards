import os
import pkg_resources
import re

from collections import namedtuple
from mako.template import Template as MakoTemplate

CardRes = namedtuple('CardRes', ['card', 'success', 'last_pos'])

class WordTooLongException(Exception):
    pass

class DescriptionTooLongException(Exception):
    pass


class TextLine:

    def __init__(self, max_len):
        self.max_len = max_len
        self.text = ''
        self._len = 0

    def __len__(self):
        return self._len

    def try_add_word(self, word):
        new_len = self._len + len(word) + 1 if self.text else len(word)
        if new_len > self.max_len:
            return False
        else:
            self.text = self.text + ' ' + word if self.text else word
            self._len = new_len
            return True

class LineGroup:

    def __init__(self, max_len, max_lines):
        self.max_len = max_len
        self.max_lines = max_lines
        self.lines = []

    def try_add_word(self, word):
        if len(word) > self.max_len:
            raise WordTooLongException

        if not self._last_line().try_add_word(word):
            if self.try_add_line():
                self._last_line().try_add_word(word)
            else:
                return False

        return True

    def try_add_line(self):
        if len(self.lines) < self.max_lines:
            self.lines.append(self._new_line())
            return True
        return False

    def _last_line(self):
        if not self.lines:
            self.try_add_line()
        return self.lines[-1]

    def _new_line(self):
        return TextLine(self.max_len)

    def to_string(self):
        return [l.text for l in self.lines]


class SpellCardTemplate:

    _BREAKS = re.compile('(?P<word>.*?)(?P<seperator>[ (\n)])')

    def __init__(self, template, characters_per_line, lines_per_card):
        self.template = template
        self.characters_per_line = characters_per_line
        self.lines_per_card = lines_per_card

    def render(self, card_class, spell, start_pos=0):
        template = MakoTemplate(
            filename=pkg_resources.resource_filename(
                'spellcards',
                os.path.join(
                    'cards/templates/',
                    self.template
                )
            )
        )
        lines, partial_res = self._create_description_lines(spell.description[start_pos:])
        rendered_template = template.render(spell=spell, lines=lines, card_class=card_class)
        return CardRes(rendered_template, *partial_res[1:])

    def _create_description_lines(self, text):
        lines = LineGroup(self.characters_per_line, self.lines_per_card)
        for word_group in self._BREAKS.finditer(text + ' '):
            word, separator = word_group.groups()

            if not lines.try_add_word(word):
                return lines.to_string(), CardRes(None, False, word_group.span()[0])

            if separator == '\n':
                lines.try_add_line()

        return lines.to_string(), CardRes(None, True, word_group.span()[1])

CardFront = SpellCardTemplate('front.svg', 48, 22)
