import json

from django.db import models

from farm.models import Farm, Field

class Scenario(models.Model):
    '''an estimation of profit and risk'''
    name = models.CharField(max_length=32, default='', blank=True)

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)

    the_nets = models.CharField(max_length=2048)
    the_histogram = models.CharField(max_length=2048)

    def setNets(self, nets):
        self.the_nets = json.dumps(nets)
        self.save()

    def getNets(self):
        return json.loads(self.the_nets)

    def setHistogram(self, histogram):
        self.the_histogram = json.dumps(histogram)
        self.save()

    def getHistogram(self):
        return json.loads(self.the_histogram)

    def __str__(self):
        if self.name:
            return '{}:{}'.format(self.farm.name, self.name)
        else:
            return '{}:scenario_{}'.format(self.farm.name, self.id)

    class Meta:
        pass


class Crop(models.Model):
    '''information about a crop for a scenario'''
    name = models.CharField(max_length=32)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)

    acres = models.PositiveSmallIntegerField()

    the_nets = models.CharField(max_length=2048)
    mean = models.FloatField()
    the_box = models.CharField(max_length=1024)

    def setNets(self, nets):
        self.the_nets = json.dumps(nets)
        self.save()

    def getNets(self):
        return json.loads(self.the_nets)

    def setBox(self, box):
        self.the_box = json.dumps(box)
        self.save()

    def getBox(self):
        return json.loads(self.the_box)

    def __str__(self):
        return '{}:{}'.format(self.scenario, self.name)

    class Meta:
        pass


class Price(models.Model):
    '''a distribution of prices'''
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)

    # store json list of prices
    the_prices = models.CharField(max_length=1024)

    def setPrices(self, prices):
        self.the_prices = json.dumps(prices)
        self.save()

    def getPrices(self):
        return json.loads(self.the_prices)

    def __str__(self):
        return 'price_{}_{}'.format(self.crop, self.id)

    class Meta:
        pass


class Yield(models.Model):
    '''a distribution of yields'''
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)

    # store json list of yields
    the_yields = models.CharField(max_length=1024)

    def setYields(self, yields):
        self.the_yields = json.dumps(yields)
        self.save()

    def getYields(self):
        return json.loads(self.the_yields)

    def __str__(self):
        return 'yield_{}_{}'.format(self.crop, self.id)

    class Meta:
        pass


class Cost(models.Model):
    '''a scalar of cost per acre'''
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)

    cost = models.FloatField()

    def __str__(self):
        return 'cost_{}_{}'.format(self.crop, self.id)

    class Meta:
        pass
