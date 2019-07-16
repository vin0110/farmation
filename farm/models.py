import json

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Farm(models.Model):
    '''specifics of a farm'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    crops = models.CharField(max_length=1024)

    def fields(self):
        return Field.objects.filter(farm=self)

    def getCrops(self):
        return json.loads(self.crops)

    def addCrops(self, crop):
        pass

    def rmCrops(self, crop):
        pass

    def __str__(self):
        return self.name

    @classmethod
    def create1KFarm(cls, user):
        '''create a 1000-acre farm'''
        farm = Farm(user=user,
                    name="Thousand-Acre Farm",
                    crops=json.dumps(settings.CROPS))
        farm.save()
        for i in range(10):
            Field.objects.create(
                farm=farm,
                name="field {}".format(i),
                acreage=100)
        return farm

    class Meta:
        pass


class Field(models.Model):
    '''specifics of a field in a farm'''
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
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
