from django.db import models

class Farm(models.Model):
    '''specifics of a farm'''
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    def fields(self):
        return Field.objects.filter(farm=self)

    def __str__(self):
        return self.name

    class Meta:
        pass

class Field(models.Model):
    '''specifics of a field in a farm'''
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=True, default='')

    acreage = models.PositiveSmallIntegerField()
