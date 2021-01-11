# Generated by Django 3.1.5 on 2021-01-10 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_viewer', '0005_auto_20210108_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='ad',
            name='closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ad',
            name='closing_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='searchphrases',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
