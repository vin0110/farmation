# Generated by Django 2.2.4 on 2019-11-04 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('optimizer', '0014_auto_20191104_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='priceorder',
            name='safety',
        ),
    ]