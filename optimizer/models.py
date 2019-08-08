import json

from django.db import models

from .analyze import analyzeScenario, describeData, mkHistogram


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


class Scenario(models.Model):
    '''an estimation of profit and risk'''
    name = models.CharField(max_length=32, default='', blank=True)

    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE,
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
            crops.append(dict(name=crop.data.name,
                              lo=crop.lo_acres,
                              hi=crop.hi_acres))

        mean, std, q1, q2, q3 = analyzeScenario(crops)
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


class AbstractCrop(models.Model):
    '''generic information about a crop for a scenario and a farm'''
    data = models.ForeignKey(CropData, on_delete=models.CASCADE)

    # zero is placeholder for area, but it means NO LIMIT for lo, hi limits
    lo_acres = models.PositiveSmallIntegerField(default=0)
    hi_acres = models.PositiveSmallIntegerField(default=0)

    yield_override = models.FloatField(default=1.0)
    cost_override = models.FloatField(default=0.0)

    def __str__(self):
        return self.data.name

    class Meta:
        abstract = True
        ordering = ('id', )


class Crop(AbstractCrop):
    '''Scenario crop object'''
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE,
                                 related_name='crops')

    def __str__(self):
        return "{}:{}".format(self.data.name, self.scenario.name)


class FarmCrop(AbstractCrop):
    '''crop that is allowed in this farm'''
    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE,
                             related_name='crops')


class PriceOverride(models.Model):
    '''hold price override info for a crop in a scenario'''
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE,
                             related_name='price_overrides')

    units = models.PositiveSmallIntegerField(default=0)
    price = models.FloatField(default=0.0)

    def __str__(self):
        return '{}:{}'.format(self.crop.data.name, self.crop.scenario.name)
