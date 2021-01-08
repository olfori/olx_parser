from django.db import models


class Ad(models.Model):                                 # ОЛХ объявления в БД
    id = models.BigIntegerField(primary_key=True, unique=True)         # id
    title = models.CharField(max_length=180)        # название обьявл
    price = models.FloatField()                     # цена
    link = models.URLField(max_length=180)          # ссылка
    date = models.DateTimeField()                   # дата создания обьявл

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class SearchPhrases(models.Model):                  # Поисковые запросы в БД
    id = models.AutoField(primary_key=True)         # id запроса
    phrase = models.CharField(max_length=180, unique=True)  # название фразы
    ads = models.ManyToManyField(Ad)

    class Meta:
        ordering = ['phrase']

    def __str__(self):
        return self.phrase
