# Generated by Django 2.2.4 on 2019-11-06 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('optimizer', '0016_auto_20191104_1636'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenario',
            name='max_expense',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='max_partition',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='max_triangle',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='mean_expense',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='mean_partition',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='mean_triangle',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='min_expense',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='min_partition',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='min_triangle',
        ),
    ]
