# Generated by Django 2.2.3 on 2019-07-15 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optimizer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='mean',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='q1',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='q3',
            field=models.FloatField(default=0.0),
        ),
    ]
