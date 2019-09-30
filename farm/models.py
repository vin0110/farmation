from django.db import models
from django.contrib.auth.models import User


class Farm(models.Model):
    '''specifics of a farm'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    max_expense = models.FloatField(default=0.0)

    def fields(self):
        return Field.objects.filter(farm=self)

    def __str__(self):
        return self.name

    def acreage(self):
        acreage = 0
        for field in self.fields.all():
            acreage += field.acreage
        return acreage

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

    class Meta:
        pass
