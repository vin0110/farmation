import json

from django.db import models

from .analyze import analyzeScenario


class CropData(models.Model):
    '''hold data about a crop'''
    name = models.CharField(max_length=32)
    # hold the the per acre unit
    unit = models.CharField(max_length=32)  # ie, bushel

    # data stored as json
    prices = models.CharField(max_length=4096, default='')
    yields = models.CharField(max_length=4096, default='')
    cost = models.FloatField(default=0.0)

    def gross(self):
        p = json.loads(self.prices)
        y = json.loads(self.yields)
        gross_triangle = [p[i] * y[i] for i in range(3)]

        return map(lambda x: round(x, 2), gross_triangle)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cropdata"


class Scenario(models.Model):
    '''an estimation of profit and risk'''
    name = models.CharField(max_length=32, default='', blank=True)

    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE,
                             related_name='scenarios')

    # analyzed
    min_triangle = models.CharField(max_length=512, default='')
    min_partition = models.CharField(max_length=512, default='')
    min_expense = models.FloatField(default=0.0)
    mean_triangle = models.CharField(max_length=512, default='')
    mean_partition = models.CharField(max_length=512, default='')
    mean_expense = models.FloatField(default=0.0)
    max_triangle = models.CharField(max_length=512, default='')
    max_partition = models.CharField(max_length=512, default='')
    max_expense = models.FloatField(default=0.0)

    def analyzeScenario(self):
        res = analyzeScenario(self.crops.all())
        if res is None:
            self.min_triangle = ''
            self.min_partition = ''
            self.min_expense = 0.0
            self.mean_triangle = ''
            self.mean_partition = ''
            self.mean_expense = 0.0
            self.max_triangle = ''
            self.max_partition = ''
            self.max_expense = 0.0
        else:
            self.min_triangle = json.dumps(res[0][0])
            self.min_partition = json.dumps(res[0][1])
            self.min_expense = json.dumps(res[0][2])
            self.mean_triangle = json.dumps(res[1][0])
            self.mean_partition = json.dumps(res[1][1])
            self.mean_expense = json.dumps(res[1][2])
            self.max_triangle = json.dumps(res[2][0])
            self.max_partition = json.dumps(res[2][1])
            self.max_expense = json.dumps(res[2][2])
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
    data = models.ForeignKey(CropData, on_delete=models.CASCADE,)

    # zero is placeholder for area, but it means NO LIMIT for lo, hi limits
    lo_acres = models.PositiveSmallIntegerField(default=0)
    hi_acres = models.PositiveSmallIntegerField(default=0)

    price_override = models.CharField(max_length=128, default='')
    yield_override = models.CharField(max_length=128, default='')
    cost_override = models.FloatField(default=0.0)

    def gross(self):
        p = json.loads(self.prices())
        y = json.loads(self.yields())
        return [p[i] * y[i] for i in range(3)]

    def prices(self):
        if self.isPriceOverride():
            return self.price_override
        else:
            return self.data.prices

    def yields(self):
        if self.isYieldOverride():
            return self.yield_override
        else:
            return self.data.yields

    def isOverride(self):
        '''checks the three parts of the gross revenue'''
        if self.price_override != '' or self.yield_override != '' or\
           self.cost_override != 0.0:
            return True
        else:
            return False

    def isPriceOverride(self):
        return self.price_override != ''

    def isYieldOverride(self):
        return self.yield_override != ''

    def isCostOverride(self):
        return self.cost_override != 0.0

    def isLimitOverride(self):
        return self.lo_acres != 0 or self.hi_acres != 0

    def limits(self):
        return (self.lo_acres, self.hi_acres)

    def show_limits(self):
        lo, hi = self.limits()
        return '{} - {}'.format(lo, hi if hi else "&infin;")

    class Meta:
        abstract = True
        ordering = ('id', )


class FarmCrop(AbstractCrop):
    '''crop that is allowed in this farm'''
    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE,
                             related_name='crops')

    def prices(self):
        if self.isPriceOverride():
            return self.price_override
        else:
            return self.data.prices

    def yields(self):
        if self.isYieldOverride():
            return self.yield_override
        else:
            return self.data.yields

    def cost(self):
        if self.cost_override != 0.0:
            return self.cost_override
        else:
            return self.data.cost

    def __str__(self):
        return "{}:{}".format(self.data.name, self.farm.name)


class Crop(AbstractCrop):
    '''Scenario crop object'''
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE,
                                 related_name='crops')
    farmcrop = models.ForeignKey(FarmCrop, on_delete=models.CASCADE)

    def prices(self):
        if self.isPriceOverride():
            return self.price_override
        else:
            return self.farmcrop.prices()

    def yields(self):
        if self.isYieldOverride():
            return self.yield_override
        else:
            return self.farmcrop.yields()

    def cost(self):
        if self.cost_override != 0.0:
            return self.cost_override
        else:
            return self.farmcrop.cost()

    def limits(self):
        self.farmcrop
        flo, fhi = self.farmcrop.lo_acres, self.farmcrop.hi_acres
        lo, hi = self.lo_acres, self.hi_acres

        if lo > 0:
            if flo > 0:
                lo = max(lo, flo)
        else:                   # lo == 0
            lo = flo

        if hi > 0:
            if fhi > 0:
                hi = min(hi, fhi)
        else:                   # hi == 0
            hi = fhi

        return (lo, hi)

    def __str__(self):
        return "{}:{}".format(self.data.name, self.scenario.name)


class PriceOrder(models.Model):
    '''hold price order info for a crop in a scenario'''
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE,
                             related_name='price_overrides')

    units = models.PositiveSmallIntegerField(default=0)
    price = models.FloatField(default=0.0)

    safety = models.PositiveSmallIntegerField(default=50)
    factor = models.FloatField(default=1.0)

    def __str__(self):
        return '{}:{}'.format(self.crop.data.name, self.crop.scenario.name)
