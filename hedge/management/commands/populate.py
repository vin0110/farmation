import sys
# import os
import csv
import datetime

from django.core.management.base import BaseCommand

from pathlib import Path

DIR = Path(__file__).resolve().parent

from hedge.models import (
    Location,
    Price,
    Future,
)


class Command(BaseCommand):
    '''
    show session list
    '''

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true',
                            help='show full json data')
        parser.add_argument('--start', type=int, default=0,
                            help='set starting point')
        parser.add_argument('which', type=str,
                            help='which model (mars, corn, wheat, soy)')
        parser.add_argument('filename', type=str,
                            help='CSV input file')

    def handle(self, *args, **kwargs):
        # test = kwargs['test']
        # start = kwargs['start']

        which = kwargs['which']
        fn = kwargs['filename']

        if fn == '-':
            f = sys.stdin
        else:
            f = open(fn, 'r')
        reader = csv.reader(f)

        if which == 'mars':
            self.do_mars(reader)
        else:
            if which == 'corn':
                crop = "C"
            elif which == 'wheat':
                crop = "W"
            elif which.startswith('soy'):
                crop = "S"
            else:
                raise KeyError('unknown which: ' + which)
            self.do_cme(reader, crop)

    def do_mars(self, reader):

        reader.__next__()       # skip header
        for row in reader:
            date = row[0]
            kind = row[2]
            crop = row[3]
            price = float(row[5])
            name = row[6]

            try:
                loc = Location.objects.get(name=name)
            except Location.DoesNotExist:
                if kind == 'elevator':
                    k = "E"
                elif kind == 'feed_mill':
                    k = "M"
                elif kind == 'soybeans_processor':
                    k = "S"
                else:
                    raise Location.DoesNotExist('kind not found: ' + kind)

                loc = Location.objects.create(
                    name=name,
                    kind=k)

            d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            Price.objects.get_or_create(
                date=d,
                location=loc,
                crop=crop.upper()[0],
                price=price)

    def do_cme(self, reader, crop):
        cnt = 0
        reader.__next__()       # skip header
        for row in reader:
            date = row[-1]
            year = int(row[0])
            month = int(row[1])
            open_ = float(row[2])/100.
            close = float(row[3])/100.

            d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            f, new_ = Future.objects.get_or_create(
                date=d,
                year=year,
                month=month,
                crop=crop,
                open=open_,
                close=close)

            cnt += 1
            if new_:
                sys.stderr.write('*')
            if cnt % 1000 == 0:
                sys.stderr.write('|')
            elif cnt % 100 == 0:
                sys.stderr.write('.')
