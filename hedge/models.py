import datetime
import calendar

from django.db import models


LOCATION_CHOICES = (
    ('E', 'elevator'),
    ('M', 'feed mill'),
    ("S", 'soybeans processor'),
)


class Location(models.Model):
    """locations of grain elevators and feed mills;
    special 'location' for CME"""
    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=1, choices=LOCATION_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        pass


CROP_CHOICES = (
    ("C", 'corn'),
    ("W", 'wheat'),
    ("S", 'soybeans'),
)


class PriceManager(models.Manager):
    def get_by_date(self, date, crop, location, days=3):
        '''get by date; with in +/- days'''
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        crop_index = crop.upper()[0]
        try:
            return Price.objects.get(
                date=date,
                crop=crop_index,
                location=location)
        except Price.DoesNotExist:
            offset = datetime.timedelta(days=days)
            prices = Price.objects.filter(crop=crop_index, location=location)
            prices = prices.filter(date__gte=date - offset)
            prices = prices.filter(date__lte=date + offset)
            cnt = prices.count()
            if cnt == 0:
                raise KeyError('no price at date')
            return prices[cnt//2]


class Price(models.Model):
    """holds MARS and CME price data"""
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    crop = models.CharField(max_length=1, choices=CROP_CHOICES)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    objects = PriceManager()

    def __str__(self):
        return f'{self.crop}:{self.location}:{self.date}'

    class Meta:
        ordering = ('date', )


class FutureManager(models.Manager):
    def get_by_date(self, date, crop, year, month, days=3):
        '''get by date; with in +/- days'''
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        crop_index = crop.upper()[0]
        try:
            return Future.objects.get(
                date=date,
                crop=crop_index,
                year=year,
                month=month)
        except Future.DoesNotExist:
            offset = datetime.timedelta(days=days)
            futures = Future.objects.filter(
                crop=crop_index,
                year=year,
                month=month
            )
            futures = futures.filter(date__gte=date - offset)
            futures = futures.filter(date__lte=date + offset)
            cnt = futures.count()
            if cnt == 0:
                raise KeyError('no future at date')
            return futures[cnt//2]


class Future(models.Model):
    """holds MARS and CME future data"""
    date = models.DateField()
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    crop = models.CharField(max_length=1, choices=CROP_CHOICES)
    open = models.DecimalField(max_digits=5, decimal_places=2)
    close = models.DecimalField(max_digits=5, decimal_places=2)

    objects = FutureManager()

    def month_name(self):
        return calendar.month_name[self.month]

    def month_abbr(self):
        return calendar.month_abbr[self.month]

    def __str__(self):
        return f'{self.crop}:{self.year}:{self.month}:{self.date}'

    class Meta:
        ordering = ('date', )
