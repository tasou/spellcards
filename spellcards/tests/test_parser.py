from spellcards.parser import page

import pytest

pages = {
    'index': open('./include/index.html', 'r').read(),
    'spell_list': open('./include/spell_list.html', 'r').read(),
    'spell': open('./include/spell.html', 'r').read()
}

@pytest.fixture(autouse=True)
def mock_index_page(mocker, monkeypatch):

    def get_page_text(page):
        request_mock = mocker.Mock()
        request_mock.read.return_value.decode.return_value = pages[page]
        return request_mock

    monkeypatch.setattr(page.request, 'urlopen', get_page_text)

def test_requires_load(mocker):

    class TestClass(page.Page):

        @page.property_requires_load
        def test_property(self):
            pass

    test_obj = TestClass('something.com')
    test_obj._load = mocker.Mock()

    _ = test_obj.test_property
    _ = test_obj.test_property
    _ = test_obj.test_property

    assert test_obj._load.call_count == 1


def test_index_page():
    index_page = page.IndexPage('index')
    assert index_page.spell_page_urls == [
        'http://paizo.com/pathfinderRPG/prd/coreRulebook/spellLists.html',
        'http://paizo.com/pathfinderRPG/prd/advancedClassGuide/spells/spellLists.html',
        'http://paizo.com/pathfinderRPG/prd/advancedPlayersGuide/advancedSpellLists.html',
        'http://paizo.com/pathfinderRPG/prd/advancedRaceGuide/spellLists.html',
        'http://paizo.com/pathfinderRPG/prd/occultAdventures/spellLists.html',
        'http://paizo.com/pathfinderRPG/prd/ultimateCombat/ultimateCombatSpellLists.html',
        'http://paizo.com/pathfinderRPG/prd/ultimateMagic/ultimateMagicSpellLists.html'
    ]

def test_spell_list():
    spell_list_page = page.SpellListPage('spell_list')
    spells = spell_list_page.spells_urls
    assert 'http://paizo.com/pathfinderRPG/prd/coreRulebook/spells/fireball.html#fireball' in spells
    assert len(spells) == 1041

def test_spell_short_descriptions():
    spell_list_page = page.SpellListPage('spell_list')
    descriptions = spell_list_page.spell_short_descriptions
    assert '1d6 damage per level, 20-ft. radius.' in descriptions
    assert len(descriptions) == 1041

@pytest.fixture
def spell_page():
    sample_spell_page = page.SpellPage('spell', 'description')
    return sample_spell_page

def test_spell_name(spell_page):
    assert spell_page.name == 'Fireball'

def test_school_subschool(spell_page):
    assert spell_page.school == ('evocation', 'fire')

def test_level(spell_page):
    assert spell_page.level == [('sorcerer', 3), ('wizard', 3)]

def test_casting_time(spell_page):
    assert spell_page.casting_time == '1 standard action'

def test_components(spell_page):
    assert spell_page.components == 'V, S, M (a ball of bat guano and sulfur)'

def test_area(spell_page):
    assert spell_page.area == '20-ft.-radius spread'

def test_duration(spell_page):
    assert spell_page.duration == 'instantaneous'

def test_save(spell_page):
    assert spell_page.saving_throw == [('Reflex', 'half'), ('Spell Resistance', True)]

def test_description(spell_page):
    assert spell_page.description.startswith('A fireball spell generates a searing explosion of flame that detonates with a low roar and deals 1d6 points of fire damage')
    assert spell_page.description.endswith('lead, gold, copper, silver, and bronze. If the damage caused to an interposing barrier shatters or breaks through it, the fireball may continue beyond the barrier if the area permits; otherwise it stops at the barrier just as any other spell effect does.')
