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

from bs4 import BeautifulSoup
from requests.utils import quote


URL_S = 'https://www.olx.ua/list/q-'
URL_E = '/?search%5Border%5D=filter_float_price%3Aasc'
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


class OLXDateConverter():
    """Convert date: '19 янв' in datetime.date(2021, 01, 19)"""

    def __init__(self, date):
        self.date = date.lower().split()
        self.y = None
        self.m = None
        self.d = None

    def set_day(self):
        if self.date[0].isnumeric:
            self.d = int(self.date[0])

    def set_month(self):
        M_LIST = ['янв', 'февр', 'март', 'апр', 'май', 'июнь',
                  'июль', 'авг', 'сен', 'окт', 'нояб', 'дек']

        month = self.date[1][:-1]
        for i, m in enumerate(M_LIST):
            if month in m:
                self.m = i+1
                break

    def set_year(self):
        self.y = dt.date.today().year
        if dt.date.today().month in [1, 2]:
            if self.m in [11, 12]:
                self.y -= 1

    def get_date(self):
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

    def has_result(self):
        if self.get_name() is not None:
            return True
        return False

    def get_id(self):
        id_ = self.block.select('table.breakword')
        if len(id_) > 0:
            id_ = id_[0]['data-id']
        return int(id_)

    def get_name(self):
        name = self.block.select('a.detailsLink > strong')
        if len(name) > 0:
            self.has_result = True
            name = name[0].contents[0]
        else:
            name = None
        return name

    def get_price(self):
        price = self.block.select('p.price > strong')
        if len(price) > 0:
            price = price[0].get_text().split()
            if price[0].isnumeric():
                pr = price[0]
                if price[1].isnumeric():
                    pr += price[1]
                price = int(pr)
            else:
                price = 0
        else:
            price = 0
        return price

    def get_date(self):
        date = self.block.select('small.breadcrumb > span')[1].get_text()
        od = OLXDateConverter(date)
        return od.get_date()

    def get_city(self):
        city = self.block.select('small.breadcrumb > span')[0].get_text()
        return city.split(',')[0]

    def get_link(self):
        link = self.block.select('a.detailsLink')
        if len(link) > 0:
            link = link[0]['href']
        return link

    def get_result(self):
        res = {'id': self.get_id(),
               'title': self.get_name(),
               'price': self.get_price(),
               'date': self.get_date(),
               'city': self.get_city(),
               'link': self.get_link(),
               }
        return res


class OLXParser:
    '''Class for parsing OLX site'''

    def __init__(self):
        self.parse_phrase = ''      # Запрос для поиска на ОЛХ
        self.pager_max = 0          # Макс. пейджер на 1-й стр
        self.soup = None            # Ответ в виде супа HTML
        self.all_blocks = []        # Список с полученной инфой

        self.ad_manager = None      # менеджер БД обьявлений

    def parse_all(self):
        '''Основной метод - парсит все страницы по запросу'''
        if self.parse_phrase == '':
            return
        self.all_blocks = []        # Обнулил список с принятой инфой
        self.parse_first_page()     # парсинг 1-й старницы
        self.get_all_page_blocks()  # Получаю данные с остальных стр.

    def parse_first_page(self):
        """парсинг первой страницы с выдачей по поисковой фразе"""
        self.get_html_soup(1)            # Получ ответ с 1-й страницы
        self.pager_max = self.get_pager_max()   # Узнал число страниц
        print('pages = ', self.pager_max, 'parse_phrase', self.parse_phrase)
        self.get_blocks()           # Получ данные с 1-й страницы

    def get_html_soup(self, page_num):
        '''Загружаю с ОЛХ HTML страницу с выдачей обьявлений'''
        link_page_num = ''
        if page_num > 1:
            link_page_num = '&page=' + str(page_num)
        url = URL_S + quote(self.parse_phrase) + URL_E + link_page_num

        response = requests.get(url, headers=HEADERS)
        self.soup = BeautifulSoup(response.content, 'html.parser')

    def get_pager_max(self):
        '''Достаю максимальное значение пейджера'''
        pager = self.soup.select('span.item > a > span')
        pager_max = 1
        if len(pager) > 0:
            len_pager = len(pager)-1
            pager_max = pager[len_pager].contents[0]
        return int(pager_max)

    def get_blocks(self):
        '''Получаю данные о каждом обьявлении - достаю из супа'''
        table = self.soup.find('table', 'fixed offers breakword redesigned')
        if table is not None:
            blocks = table.select('tr.wrap > td > div.offer-wrapper')
            for block in blocks:
                b = ParseBlock(block)
                if b.has_result():
                    res = b.get_result()
                    self.all_blocks.append(res)
                    if self.ad_manager is not None:
                        self.ad_manager.update_or_create(
                            res, self.parse_phrase)
                    # print(res)

    def get_all_page_blocks(self):
        '''Парсинг каждой страницы с обьявлениями после первой'''
        for i in range(2, self.pager_max + 1):
            self.get_html_soup(i)
            self.get_blocks()
            print('get ', i, ' pages from OLX.ua')
            time.sleep(2)

    def parsing(self, parse_phrase):
        '''Основной метод сбора данных'''
        self.parse_phrase = parse_phrase
        self.parse_all()


def tst1():
    link = 'https://www.olx.ua/list/q-%D0%B0%D0%B2%D1%82%D0%BE/'


if __name__ == '__main__':
    op = OLXParser()
    op.parsing('робот пылесос')
    #oc = OLXDateConverter('10 дек')
    # print(oc.get_date())
