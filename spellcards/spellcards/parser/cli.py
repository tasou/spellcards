import click
import json
import logging
import tqdm

from itertools import chain

from spellcards.parser.pages import IndexPage, SpellListPage, SpellPage, ParsingException

logger = logging.Logger('spell_parser')
logger.setLevel(logging.INFO)

@click.command()
@click.argument('output_file', type=click.File(mode='w'))
@click.option('--spell_root', default='http://paizo.com/pathfinderRPG/prd/')
@click.option('--debug', is_flag=True)
def download_spells(output_file, spell_root, debug):

    if debug:
        logger.setLevel(logging.DEBUG)
        import pdb
        pdb.set_trace()

    logger.info('Starting download')
    logger.debug('Loading index page %s', spell_root)
    index = IndexPage(spell_root)
    spell_lists = index.spell_page_urls
    logger.debug('Loading %s spell list pages: \n%s', len(spell_lists), '\n'.join(spell_lists))
    spell_lists = map(SpellListPage, spell_lists)
    spell_lists = list(chain(*map(lambda spell_list: spell_list.spells, spell_lists)))

    def load_each(spell_info):
        try:
            return SpellPage(*spell_info).load_spell()
        except Exception:
            logger.exception('Failed to parse %s', spell_info[0])
    spell_pages = map(load_each, spell_lists)

    logger.info('Loading spells')
    spells = [spell for spell in tqdm.tqdm(spell_pages, total=len(spell_lists))]
    spells = list(filter(lambda x: x is not None, spells))

    logger.info('Writing to file')
    json.dump(spells, output_file)

if __name__ == "__main__":
    download_spells()
