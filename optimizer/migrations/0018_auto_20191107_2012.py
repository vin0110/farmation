# Generated by Django 2.2.4 on 2019-11-07 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optimizer', '0017_auto_20191106_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='priceorder',
            name='safety',
            field=models.CharField(default='Medium', max_length=10),
        ),
    ]