import datetime

from django.db import models

from django.db.models import Count
from django.db.models import Q


class Ad(models.Model):                             # ОЛХ объявления в БД
    id = models.BigIntegerField(primary_key=True, unique=True)     # id
    title = models.CharField(max_length=180)        # название обьявл
    price = models.FloatField()                     # цена
    date = models.DateField()                       # дата создания обьявл
    city = models.CharField(null=True, max_length=50)
    link = models.URLField(max_length=180)          # ссылка
    closed = models.BooleanField(default=False)     # закрыто ли обьявление
    closing_date = models.DateField(null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class SearchPhrases(models.Model):                  # Поисковые запросы в БД
    phrase = models.CharField(max_length=180, unique=True)  # название фразы
    ads = models.ManyToManyField(Ad, blank=True)

    class Meta:
        ordering = ['phrase']

    def __str__(self):
        return self.phrase


class SPManager():

    def get_by_phrase(self, search_phrase: str) -> SearchPhrases:
        sp_obj = SearchPhrases.objects.get(
            phrase=search_phrase)
        return sp_obj

    def get_or_create(self, search_phrase: str) -> SearchPhrases:
        """Get or create instance of an SearchPhrases"""
        sp_obj, created = SearchPhrases.objects.get_or_create(
            phrase=search_phrase,
            defaults={'phrase': search_phrase},
        )
        return sp_obj

    def get_all(self) -> list:
        sp = SearchPhrases.objects.annotate(
            total_ads=Count(
                'ads',
                filter=Q(ads__closed=False)))
        sp = sp.annotate(
            total_ads_closed=Count(
                'ads',
                filter=Q(ads__closed=True)))
        return sp.values()

    def get_ads(self, sp_id: int) -> list:
        sp_obj = SearchPhrases.objects.get(pk=sp_id)
        ads = sp_obj.ads.all().order_by('price')
        return ads.values()

    def delete(self, del_id: int) -> None:
        del_obj = SearchPhrases.objects.get(pk=del_id)
        if del_obj is not None:
            del_obj.delete()

    def del_closed_ad(self, search_phrase: str) -> None:
        sp_obj = SearchPhrases.objects.get(phrase=search_phrase)
        sp_obj.ads.filter(closed=True).delete()


class AdManager():

    def update_or_create(self, ad_data: dict, search_phrase: str) -> None:
        """Update or instantiate an Ad for this SearchPhrase"""
        sp_obj = SPManager().get_or_create(search_phrase)
        ad_obj, created = Ad.objects.update_or_create(
            id=ad_data['id'],
            defaults=ad_data,
        )
        sp_obj.ads.add(ad_obj)

    def set_given_as_closed(self, id_list: list) -> None:
        """Set all given ads as closed"""
        for ad_id in id_list:
            ad = Ad.objects.get(id=ad_id)
            ad.closed = True
            ad.closing_date = datetime.date.today()
            ad.save()

    def del_old_closed(self, id_list: list) -> None:
        """Remove all specified ads if they are older than a week"""
        for ad_id in id_list:
            Ad.objects.get(id=ad_id)
