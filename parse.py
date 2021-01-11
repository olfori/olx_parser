import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = 'olx_parser.settings'
django.setup()
from parser_viewer.models import AdManager, SPManager
from parser.olx import OLXParser


op = OLXParser()
op.ad_manager = AdManager()
search_phrases = SPManager().get_all()

for sp in search_phrases:
    op.parsing(sp['phrase'])
