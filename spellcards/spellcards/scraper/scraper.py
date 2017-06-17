from ..pathfinder.caster_class import CasterClass
from ..pathfinder.spell import Spell

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


def _header_to_title(header_attribute):
    return header_attribute.title().replace('_', ' ')


def _contains_text(etree, some_str):
    return etree.xpath('//*[text()[contains(.,"{}")]]'.format(some_str))


def _get_header_value(etree, some_str):
    tag = _contains_text(etree, some_str)
    tag = [t for t in tag if t.tag == 'b']
    if tag:
        return tag[0].tail.strip(';, ')
    return ''


def spell_from_page(spell_page):
    spell_args = {}

    spell_args = parse_header(spell_args, spell_page)
    spell_args = parse_description(spell_args, spell_page)
    return Spell(**spell_args)


def parse_header(spell_args, spell_page):
    spell_header = spell_page.etree.xpath(_SPELL_HEADER_XPATH)[0]

    for header_arg in _SIMPLE_HEADER_ARGS:
        spell_args[header_arg] = _get_header_value(spell_header, _header_to_title(header_arg))

    def _try_assign(caster_class, spell_level):
        spell_level = spell_level.tail.strip(', ')
        if spell_level.isdigit():
            spell_args['level'][caster_class.name] = spell_level
            return True
        return False

    spell_args['level'] = {}
    for caster_class in CasterClass:
        spell_level_tags = _contains_text(spell_header, caster_class.name)
        for spell_level_tag in spell_level_tags:
            while spell_level_tag.text in CasterClass.__members__.keys():
                if _try_assign(caster_class, spell_level_tag):
                    break
                spell_level_tag = spell_level_tag.getnext()

    return spell_args


def parse_description(spell_args, spell_page):
    description = []
    next_node = _contains_text(spell_page.etree, 'DESCRIPTION')[0].getnext()

    while next_node.tag == 'p':
        description.append(next_node.text_content())
        next_node = next_node.getnext()

    spell_args['description'] = '\n'.join(description)
    return spell_args

