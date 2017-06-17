from urllib import request
from lxml import html

class Page:

    _BASE_URL = 'http://www.d20pfsrd.com'

    def __init__(self, url):
        self.url = url

    def load(self):
        html_str = request.urlopen(self.url).read().decode('utf-8')
        self.etree = html.fromstring(html.make_links_absolute(html_str, base_url=self._BASE_URL))
        return self


class SpellListPage(Page):

    def __init__(self, url):
        super.__init__(url, 'http://www.d20pfsrd.com')

    def load(self):
        super().load()
        self.spells = self.etree.find_class('spell')
