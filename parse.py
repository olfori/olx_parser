import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = 'olx_parser.settings'
django.setup()

from parser.olx import OLXParser
from parser_viewer.models import AdManager, SPManager


parser = OLXParser()
sp_mgr = SPManager()
ad_mgr = AdManager()
search_phrases = sp_mgr.get_all()  # Достали все поисковые фразы из БД

for i, sp in enumerate(search_phrases):       # Идем по поисковым фразам
    phrase = sp['phrase']

    parser.parsing(phrase)          # парсим фразу

    new_ads = parser.get_all_ads()  # достал все спарсенные объявы
    new_ads_id = [ad['id'] for ad in new_ads]   # list их ID
    # достал все обьявы из БД
    db_ads = sp_mgr.get_by_phrase(phrase).ads.all().values()
    db_ads_id = [ad['id'] for ad in db_ads]     # list их ID

    # нашел все ID, которые есть в БД, но нет в новом парсе
    closed_ads = list(set(db_ads_id) - set(new_ads_id))
    ad_mgr.set_given_as_closed(closed_ads)

    print('closed ads = ', len(closed_ads))

    for ad in new_ads:
        ad_mgr.update_or_create(ad, phrase)


