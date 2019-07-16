# Generated by Django 2.2.3 on 2019-07-15 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('farm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=32)),
                ('state', models.CharField(choices=[('M', 'Modified'), ('A', 'Analyzed')], default='M', max_length=1)),
                ('mean', models.FloatField()),
                ('mean_partition', models.CharField(max_length=2048)),
                ('q1', models.FloatField()),
                ('q1_partition', models.CharField(max_length=2048)),
                ('q3', models.FloatField()),
                ('q3_partition', models.CharField(max_length=2048)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scenarios', to='farm.Farm')),
            ],
        ),
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('lo_acres', models.PositiveSmallIntegerField(default=0)),
                ('hi_acres', models.PositiveSmallIntegerField(default=0)),
                ('the_prices', models.CharField(max_length=4096)),
                ('the_yields', models.CharField(max_length=4096)),
                ('cost', models.FloatField(default=-1.0)),
                ('mean', models.FloatField(default=-1.0)),
                ('std', models.FloatField(default=-1.0)),
                ('quartiles', models.CharField(default='', max_length=1024)),
                ('histogram', models.CharField(default='', max_length=2048)),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crops', to='optimizer.Scenario')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
    ]
