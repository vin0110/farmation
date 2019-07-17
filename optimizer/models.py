import json, pickle

from django.db import models
from django.conf import settings

from farm.models import Farm

from .analyze import positiveDistro, cropDistro, analyzeScenario


class Scenario(models.Model):
    '''an estimation of profit and risk'''
    name = models.CharField(max_length=32, default='', blank=True)

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE,
                             related_name='scenarios')

    state_choices = (
        ('M', 'Modified', ),
        ('A', 'Analyzed', ), )

    state = models.CharField(max_length=1,
                             choices=state_choices,
                             default='M')

    mean = models.FloatField(default=0.0)
    mean_partition = models.CharField(max_length=2048)
    q1 = models.FloatField(default=0.0)
    q1_partition = models.CharField(max_length=2048)
    q3 = models.FloatField(default=0.0)
    q3_partition = models.CharField(max_length=2048)

    def getState(self):
        index = [l for l, w in self.state_choices]
        return self.state_choices[index.index(self.state)][1]

    def analyzeScenario(self):
        crops = []
        for crop in self.crops.all():
            quartiles = crop.getQuartiles()
            crops.append(dict(mean=crop.mean,
                              q1=quartiles[0],
                              q3=quartiles[2],
                              lo=crop.lo_acres,
                              hi=crop.hi_acres))

        mean, q1, q3 = analyzeScenario(crops)
        self.mean = mean[1]
        self.mean_partition = json.dumps(mean[0])
        self.q1 = q1[1]
        self.q1_partition = json.dumps(q1[0])
        self.q3 = q3[1]
        self.q3_partition = json.dumps(q3[0])
        self.state = "A"
        self.save()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '({})'.format(self.id)

    class Meta:
        pass


class Crop(models.Model):
    '''information about a crop for a scenario'''
    name = models.CharField(max_length=32)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE,
                                 related_name='crops')

    # zero is placeholder for area, but it means NO LIMIT for lo, hi limits
    lo_acres = models.PositiveSmallIntegerField(default=0)
    hi_acres = models.PositiveSmallIntegerField(default=0)

    # instances -- set defaults
    the_prices = models.CharField(max_length=4096)
    the_yields = models.CharField(max_length=4096)
    cost = models.FloatField(default=-1.0)

    # crop statistics -- will not be known when first created
    # therefore, provide defaults
    mean = models.FloatField(default=-1.0)
    std = models.FloatField(default=-1.0)
    quartiles = models.CharField(max_length=1024, default='')
    histogram = models.CharField(max_length=2048, default='')

    def getQuartiles(self):
        return json.loads(self.quartiles)

    def getHistogram(self):
        return pickle.loads(self.histograma)

    def setPrices(self):
        stats = settings.STATS[self.name]['price']
        prices = positiveDistro(stats['mu'], stats['sigma'])
        self.the_prices = json.dumps(prices)
        self.save()

    def getPrices(self, regenerate=False):
        if not self.the_prices or regenerate:
            self.setPrices()
        return json.loads(self.the_prices)

    def setYields(self):
        stats = settings.STATS[self.name]['yield']
        yields = positiveDistro(stats['mu'], stats['sigma'])
        self.the_yields = json.dumps(yields)
        self.save()

    def getYields(self, regenerate=False):
        if not self.the_yields or regenerate:
            self.setYields()
        return json.loads(self.the_yields)

    def analyze(self):
        self.mean, self.std, quartiles, histogram\
            = cropDistro(self.getPrices(), self.getYields(), self.cost)
        self.quartiles = json.dumps(quartiles)
        self.histogram = pickle.dumps(histogram)

        self.cost = settings.STATS[self.name]['cost']

        self.save()

    def __str__(self):
        return self.name

    def farmName(self):
        '''for admin'''
        return self.scenario.farm

    def scenarioName(self):
        '''for admin'''
        return self.scenario

    def userName(self):
        '''for admin'''
        return self.scenario.farm.user

    class Meta:
        ordering = ('id', )
