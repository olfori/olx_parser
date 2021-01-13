"""OLX parser
Алгоритм:

parsing()       - метод начала парсинга
- parse_phrase      - установил запрос парсинга
- parse_all()       - парсинг всех страниц ОЛХ по заданному запросу

parse_all()     - метод парсинга всех страниц ОЛХ по заданному запросу
-                   - обнулил данные прошлого парсинга
-                   - прочитал 1-ю страницу по текущему запросу, получил данные для парсинга
-                   - читаю страницы по очереди

last_parse_data - Данные прошлого парсинга
- 

css_soup.find_all("p", class_="body strikeout")  - точное строковое значение атрибута class
css_soup.find_all("p", "body strikeout") - тоже самое

"""
import datetime as dt
import time
import requests
from random import randint as rnd

from bs4 import BeautifulSoup
from requests.utils import quote

PRINT_INFO = True

URL_S = 'https://www.olx.ua/list/q-'
URL_E = '/?search%5Border%5D=filter_float_price%3Aasc'
FMP = '&search%5Bfilter_float_price%3Afrom%5D='   # filter min price
'''
https://www.olx.ua/list/q-
search_pfrase
/?search%5Border%5D=filter_float_price%3Aasc
&search%5Bfilter_float_price%3Afrom%5D=1000
&search%5Bfilter_float_price%3Ato%5D=1999
&page=10
'''

HEADERS = {
    'User-Agent': 'Mozilla/5.0 Firefox/4.0.1',
    'Refer': 'http://google.com'
}


def print_info(search_phrase: str, page_num: int) -> None:
    if PRINT_INFO:
        print('search phrase = {0}, received {1} pages from OLX'.
              format(search_phrase, page_num))


def clean_str(s: str) -> str:
    """Clean the given string"""
    return ' '.join(s.split()).lower()


def str_to_price(str_price: str) -> int:
    price = ''
    list_price = str_price.split()
    for i, pr in enumerate(list_price):
        if pr.isnumeric():
            price += pr
        elif i == 0:
            return 0
    return int(price)


class OLXDateConverter():
    """Convert date: '19 янв' in datetime.date(2021, 01, 19)"""

    def __init__(self, date: str):
        self.date = date.lower().split()
        self.y = None
        self.m = None
        self.d = None

    def set_day(self) -> None:
        if self.date[0].isnumeric:
            self.d = int(self.date[0])

    def set_month(self) -> None:
        M_LIST = ['янв', 'февр', 'март', 'апр', 'май', 'июнь',
                  'июль', 'авг', 'сен', 'окт', 'нояб', 'дек']

        month = self.date[1][:-1]
        for i, m in enumerate(M_LIST):
            if month in m:
                self.m = i+1
                break

    def set_year(self) -> None:
        self.y = dt.date.today().year
        if dt.date.today().month in [1, 2]:
            if self.m in [11, 12]:
                self.y -= 1

    def get_date(self) -> dt:
        if len(self.date) != 2:
            return dt.date.today()

        if 'сег' in self.date[0]:
            return dt.date.today()

        if 'вче' in self.date[0]:
            return dt.date.today() - dt.timedelta(days=1)

        self.set_day()
        self.set_month()
        self.set_year()
        return dt.date(self.y, self.m, self.d)


class ParseBlock():
    """Class for parsing one block on an OLX page"""

    def __init__(self, block):
        self.block = block

    def has_result(self) -> bool:
        if self.get_name() is not None:
            return True
        return False

    def get_id(self) -> int:
        id_ = self.block.select('table.breakword')
        if len(id_) > 0:
            id_ = id_[0]['data-id']
        return int(id_)

    def get_name(self) -> str:
        name = self.block.select('a.detailsLink > strong')
        if len(name) > 0:
            self.has_result = True
            name = name[0].contents[0]
        else:
            name = None
        return name

    def get_price(self) -> int:
        price = self.block.select('p.price > strong')
        if len(price) > 0:
            price = str_to_price(price[0].get_text())
        else:
            price = 0
        return price

    def get_date(self) -> dt:
        date = self.block.select('small.breadcrumb > span')[1].get_text()
        od = OLXDateConverter(date)
        return od.get_date()

    def get_city(self) -> str:
        city = self.block.select('small.breadcrumb > span')[0].get_text()
        return city.split(',')[0]

    def get_link(self) -> str:
        link = self.block.select('a.detailsLink')
        if len(link) > 0:
            link = link[0]['href']
        return link

    def get_result(self) -> dict:
        res = {'id': self.get_id(),
               'title': self.get_name(),
               'price': self.get_price(),
               'date': self.get_date(),
               'city': self.get_city(),
               'link': self.get_link(),
               }
        return res


class RememberMax:
    """Class for calculating the maximum number"""

    def __init__(self):
        self.max_val = 0

    def calc(self, val: int) -> None:
        if val > self.max_val:
            self.max_val = val

    def get_max(self) -> int:
        return self.max_val


class OLXParser:
    '''Class for parsing OLX site'''

    def __init__(self):
        self.parse_phrase = ''      # Запрос для поиска на ОЛХ
        self.ads = []
        # self.ad_manager = None      # менеджер БД обьявлений

        self._pager_max = 0         # Макс. пейджер на 1-й стр ОЛХ
        self._page_max_price = 0
        self._phrase_max_price = 0
        self._parse_circle = 0
        self._soup = None           # Ответ в виде супа HTML
        self._blocks = None         # необработанные блоки обьявлений

    def get_all_ads(self) -> list:
        """Get all ads for a given ParsePhrase"""
        return self.ads

    def parsing(self, parse_phrase='') -> None:
        '''Основной метод сбора данных'''
        parse_phrase = clean_str(parse_phrase)
        if parse_phrase == '':
            return
        self._reset_data()
        self.parse_phrase = parse_phrase
        self._parse_all()

    def _reset_data(self) -> None:
        """Обнулил все данные парсера для нового запроса"""
        self._pager_max = 0
        self._page_max_price = 0
        self._phrase_max_price = 0
        self._parse_circle = 0
        self.ads = []

    def _parse_all(self) -> None:
        '''Основной метод - парсит все страницы по запросу'''
        self._parse_first_page()
        self._get_all_ad_blocks()
        self._is_all_pages_received()

    def _parse_first_page(self) -> None:
        """парсинг первой страницы по запросу"""
        self._get_html_soup(1)
        self._get_pager_max()

    def _get_all_ad_blocks(self) -> None:
        '''Парсинг каждой страницы с обьявлениями после первой'''
        for page_num in range(1, self._pager_max + 1):
            if page_num > 1:
                self._get_html_soup(page_num)
            self._get_ad_blocks()
            self._save_ad_blocks_data()

            pn = page_num + self._parse_circle * 25
            print_info(self.parse_phrase, pn)
            rand_time = rnd(0, 5)/10
            time.sleep(1.8 + rand_time)

    def _is_all_pages_received(self) -> None:
        if self._pager_max == 25:
            self._parse_circle += 1
            self._phrase_max_price = self._page_max_price
            self._parse_all()

    def _get_html_soup(self, page_num: int) -> None:
        '''Загружаю с ОЛХ HTML страницу с выдачей обьявлений'''
        link_page_num = ''
        fmp = ''
        if page_num > 1:
            link_page_num = '&page=' + str(page_num)
        if self._parse_circle > 0:
            fmp = FMP + str(self._phrase_max_price)
        url = URL_S + quote(self.parse_phrase) + URL_E + fmp + link_page_num

        response = requests.get(url, headers=HEADERS)
        self._soup = BeautifulSoup(response.content, 'html.parser')

    def _get_pager_max(self) -> None:
        '''Достаю максимальное значение пейджера'''
        pager = self._soup.select('span.item > a > span')
        pager_max = 1
        if len(pager) > 0:
            len_pager = len(pager)-1
            pager_max = pager[len_pager].contents[0]
        self._pager_max = int(pager_max)

    def _get_ad_blocks(self) -> None:
        table = self._soup.find('table', 'fixed offers breakword redesigned')
        self._blocks = None
        if table is not None:
            self._blocks = table.select('tr.wrap > td > div.offer-wrapper')

    def _save_ad_blocks_data(self) -> None:
        '''Получаю данные о каждом обьявлении - достаю из супа'''
        rm = RememberMax()
        for block in self._blocks:
            b = ParseBlock(block)
            if b.has_result():
                res = b.get_result()
                rm.calc(res['price'])
                self.ads.append(res)
                # if self.ad_manager is not None:
                #    self.ad_manager.update_or_create(
                #        res, self.parse_phrase)
                # print(res)
        self._page_max_price = rm.get_max()
        print('page_max_price = ', self._page_max_price)


if __name__ == '__main__':
    #op = OLXParser()
    #op.parsing('робот пылесос')
    s1, s2 = set([1, 11]), set([2, 3, 4, 5, 6, 7, 8, 9, 0])
    st = list(s1 - s2)
    print(st)
