# Generated by Django 2.2.4 on 2019-08-08 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('farm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lo_acres', models.PositiveSmallIntegerField(default=0)),
                ('hi_acres', models.PositiveSmallIntegerField(default=0)),
                ('yield_override', models.FloatField(default=1.0)),
                ('cost_override', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CropData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('unit', models.CharField(max_length=32)),
                ('prices', models.CharField(default='', max_length=4096)),
                ('yields', models.CharField(default='', max_length=4096)),
                ('cost', models.FloatField(default=0.0)),
                ('price_stats', models.CharField(default='', max_length=2048)),
                ('yield_stats', models.CharField(default='', max_length=2048)),
                ('price_histo', models.CharField(default='', max_length=2048)),
                ('yield_histo', models.CharField(default='', max_length=2048)),
            ],
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=32)),
                ('state', models.CharField(choices=[('M', 'Modified'), ('A', 'Analyzed')], default='M', max_length=1)),
                ('mean', models.FloatField(default=0.0)),
                ('mean_partition', models.CharField(max_length=2048)),
                ('q1', models.FloatField(default=0.0)),
                ('q1_partition', models.CharField(max_length=2048)),
                ('q3', models.FloatField(default=0.0)),
                ('q3_partition', models.CharField(max_length=2048)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scenarios', to='farm.Farm')),
            ],
        ),
        migrations.CreateModel(
            name='PriceOverride',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units', models.PositiveSmallIntegerField(default=0)),
                ('price', models.FloatField(default=0.0)),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_overrides', to='optimizer.Crop')),
            ],
        ),
        migrations.CreateModel(
            name='FarmCrop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lo_acres', models.PositiveSmallIntegerField(default=0)),
                ('hi_acres', models.PositiveSmallIntegerField(default=0)),
                ('yield_override', models.FloatField(default=1.0)),
                ('cost_override', models.FloatField(default=0.0)),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='optimizer.CropData')),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crops', to='farm.Farm')),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='crop',
            name='data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='optimizer.CropData'),
        ),
        migrations.AddField(
            model_name='crop',
            name='scenario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crops', to='optimizer.Scenario'),
        ),
    ]
