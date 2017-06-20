from urllib import request
from lxml import html

from ..pathfinder.caster_class import CasterClass
from ..pathfinder.spell import Spell


class Page:

    _BASE_URL = 'http://www.d20pfsrd.com'

    def __init__(self, url):
        self.url = url
        self.etree = None

    def load(self):
        if self.etree is None:
            html_str = request.urlopen(self.url).read().decode('utf-8')
            self.etree = html.fromstring(html.make_links_absolute(html_str, base_url=self._BASE_URL))
        return self


class SpellListPage(Page):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spells = []

    def load(self):
        super().load()
        self.spells = [SpellPage(s.attrib['href']) for s in self.etree.find_class('spell')]


class SpellPage(Page):

    _SPELL_HEADER_XPATH = '//article//table//td[@class="sites-layout-tile sites-tile-name-content-1"]/p[not(@class="divider")]'
    _SIMPLE_HEADER_ARGS = [
        'school',
        'casting_time',
        'components',
        'duration',
        'saving_throw',
        'spell_resistance',
        'range',
        'effect'
    ]

    def to_spell(self):
        spell_args = {}

        spell_args = self._get_name(spell_args)
        spell_args = self._parse_header(spell_args)
        spell_args = self._parse_description(spell_args)
        return Spell(**spell_args)

    def _get_name(self, spell_args):
        header_tag = self.etree.xpath('//h1')
        spell_args['name'] = header_tag[0].text
        return spell_args

    def _parse_header(self, spell_args):
        spell_header = self.etree.xpath(self._SPELL_HEADER_XPATH)[0]

        for header_arg in self._SIMPLE_HEADER_ARGS:
            spell_args[header_arg] = self._get_header_value(
                spell_header,
                self._header_to_title(header_arg)
            )
        spell_args['components'] = [c.strip('(), ') for c in spell_args['components'].split(',')]

        def _try_assign(caster_class, spell_level):
            spell_level = spell_level.tail.strip(', ')
            if spell_level.isdigit():
                spell_args['level'][caster_class.name] = spell_level
                return True
            return False

        spell_args['level'] = {}
        for caster_class in CasterClass:
            spell_level_tags = self._contains_text(spell_header, caster_class.name)
            for spell_level_tag in spell_level_tags:
                while spell_level_tag.text in CasterClass.__members__.keys():
                    if _try_assign(caster_class, spell_level_tag):
                        break
                    spell_level_tag = spell_level_tag.getnext()

        return spell_args

    def _header_to_title(self, header_attribute):
        return header_attribute.title().replace('_', ' ')

    def _get_header_value(self, etree, some_str):
        tag = self._contains_text(etree, some_str)
        tag = [t for t in tag if t.tag == 'b']
        if tag:
            return tag[0].tail.strip(';, ')
        return ''

    def _contains_text(self, etree, some_str):
        return etree.xpath('//*[text()[contains(.,"{}")]]'.format(some_str))

    def _parse_description(self, spell_args):
        description = []
        next_node = self._contains_text(self.etree, 'DESCRIPTION')[0].getnext()

        while next_node.tag == 'p':
            description.append(next_node.text_content())
            next_node = next_node.getnext()

        spell_args['description'] = '\n'.join(description)
        return spell_args
