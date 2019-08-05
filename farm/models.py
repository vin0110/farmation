import json

from django.db import models
from django.contrib.auth.models import User

from optimizer.analyze import describeData, mkHistogram


class Farm(models.Model):
    '''specifics of a farm'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    crops = models.CharField(max_length=1024)

    def fields(self):
        return Field.objects.filter(farm=self)

    def getCrops(self):
        return json.loads(self.crops)

    def addCrop(self, crop):
        crops = self.getCrops()
        if crop.lower() in crops:
            raise ValueError('crop "{}" in farm'.format(crop))
        crops.append(crop.lower())
        self.crops = json.dumps(crops)
        self.save()

    def rmCrop(self, crop):
        '''return ValueError if crop not in farm'''
        crops = self.getCrops()
        idx = crops.index(crop)
        del crops[idx]
        self.crops = json.dumps(crops)
        self.save()

    def __str__(self):
        return self.name

    def acreage(self):
        acreage = 0
        for field in self.fields.all():
            acreage += field.acreage
        return acreage

    @classmethod
    def create1KFarm(cls, user):
        '''create a 1000-acre farm'''
        farm = Farm(user=user,
                    name="Thousand-Acre Farm",
                    crops=json.dumps(['corn', 'soybeans', 'wheat']))
        farm.save()
        for n in ['one', 'two', 'three', 'four', 'five',
                  'six', 'seven', 'eight', 'nine', 'ten']:
            Field.objects.create(
                farm=farm,
                name="Field {}".format(n),
                acreage=100)
        return farm

    class Meta:
        pass


class Field(models.Model):
    '''specifics of a field in a farm'''
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE,
                             related_name='fields')
    name = models.CharField(max_length=64, blank=True, default='')

    acreage = models.PositiveSmallIntegerField()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.id)

    def farmUser(self):
        '''for admin'''
        return self.farm.user

    class Meta:
        pass


class CropData(models.Model):
    '''hold data about a crop'''
    name = models.CharField(max_length=32)
    # hold the the per acre unit
    unit = models.CharField(max_length=32)  # ie, bushel

    # data stored as json
    prices = models.CharField(max_length=4096, default='')
    yields = models.CharField(max_length=4096, default='')
    cost = models.FloatField(default=0.0)

    # holds derived stats about prices and yields (dict in json format)
    price_stats = models.CharField(max_length=2048, default='')
    yield_stats = models.CharField(max_length=2048, default='')

    # holds derived stats about prices and yields (tuple in json format)
    price_histo = models.CharField(max_length=2048, default='')
    yield_histo = models.CharField(max_length=2048, default='')

    def save(self, *args, **kwargs):
        if self.prices:
            prices = json.loads(self.prices)
            self.price_stats = json.dumps(describeData(prices))
            self.price_histo = json.dumps(mkHistogram(prices))
        if self.yields:
            yields = json.loads(self.yields)
            self.yield_stats = json.dumps(describeData(yields))
            self.yield_histo = json.dumps(mkHistogram(yields))
        super().save(*args, **kwargs)
