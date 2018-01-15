from urllib import request
from lxml import html

from itertools import product

class ParsingException(Exception): pass

def requires_load(func):
    def wrapped_func(self, *args, **kwargs):
        if not self.loaded:
            self._load()
            self.loaded = True
        return func(self, *args, **kwargs)
    return wrapped_func


def property_requires_load(func):
    return property(requires_load(func))


class Page:

    _BASE_URL = 'http://paizo.com/pathfinderRPG/prd/'

    def __init__(self, url):
        self.url = url
        self.etree = None
        self.loaded = False

    def _load(self):
        self._load_etree()
        self.loaded = True
        return

    def _load_etree(self):
        if self.etree is None:
            html_str = request.urlopen(self.url).read().decode('utf-8')
            self.etree = html.fromstring(html.make_links_absolute(html_str, base_url=self._BASE_URL))


class IndexPage(Page):

    @property_requires_load
    def spell_page_urls(self):
        return self.etree.xpath('//ul[@class="level-2"]//a[text()="Spell Lists"]/@href')


class SpellListPage(Page):

    @property_requires_load
    def spells_urls(self):
        return self.etree.xpath('//p/b/a[contains(@href,"spells/")]/@href')

    @property_requires_load
    def spell_short_descriptions(self):
        matches = self.etree.xpath('//p[b/a[contains(@href,"spells/")]]')
        return [m.text_content()[len(m.getchildren()[0].text_content()):].strip(': ') for m in matches]  # Don't really like this, but I'm a little bit sick of it for now.

class SpellPage(Page):

    def __init__(self, url, short_description):
        self.short_description = short_description
        super().__init__(url)

    def _get_attribute(self, name):
        blocks = self.etree.xpath('//p[@class="stat-block-1"][b[text()="{}"]]/text()'.format(name))
        return self._assert_one_result(name, blocks)

    @staticmethod
    def _assert_one_result(field, result):
        if len(result) != 1:
            raise ParsingException('Found {} "{}" blocks'.format(len(result), field))
        return result[0].strip()

    @property_requires_load
    def name(self):
        name_blocks = self.etree.xpath('//p[@class="stat-block-title"]/b/text()')
        return self._assert_one_result('Name', name_blocks)

    @property_requires_load
    def school(self):
        school, subschool = self.etree.xpath('//p[@class="stat-block-1"][b[text()="School"]]/text()')[0].split()
        subschool = subschool.strip('[];')
        return (school, subschool)

    @property_requires_load
    def level(self):
        classes, level = self.etree.xpath('//p[@class="stat-block-1"][b[text()="Level"]]/text()')[1].split()
        classes = classes.strip().split('/')
        return list(product(classes, [int(level)]))

    @property_requires_load
    def casting_time(self):
        return self._get_attribute('Casting Time')

    @property_requires_load
    def components(self):
        return self._get_attribute('Components')

    @property_requires_load
    def range(self):
        return self._get_attribute('Range')

    @property_requires_load
    def area(self):
        return self._get_attribute('Area')

    @property_requires_load
    def duration(self):
        return self._get_attribute('Duration')

    @property_requires_load
    def saving_throw(self):
        save_type = self.etree.xpath('//p[@class="stat-block-1"][b[text()="Saving Throw"]]/a/text()')

        save_results = self.etree.xpath('//p[@class="stat-block-1"][b[text()="Saving Throw"]]/text()')[1:]
        save_results = list(map(lambda x: x.strip('; '), save_results))
        save_results[-1] = save_results[-1] == 'yes'

        return list(zip(save_type + ['Spell Resistance'], save_results))

    @property_requires_load
    def description(self):
        description = self.etree.xpath('//div[@class="body"]/p[not(@class = "stat-block-1") and not(@class = "stat-block-title")]')
        description = '/n/n'.join([d.text_content() for d in description])
        return description
