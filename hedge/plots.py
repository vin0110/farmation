import datetime
import statistics

from .models import (
    Price,
    Future,
)


def quantity_plot(crop, location, hday, hmon, rday, rmon, month,
                  quantities=None, years=None):
    '''return list of hedge data points varying quantity'''
    # assume one date and multiple quantities
    if not years:
        years = range(2010, 2020)

    if not quantities:
        quantities = [0, 100]

    df = {}
    for y in years:
        quants = {}
        for q in quantities:
            hdate = datetime.date(y, hmon, hday)
            rdate = datetime.date(y, rmon, rday)
            try:
                mars = Price.objects.get_by_date(rdate, crop, location)
                sell = Future.objects.get_by_date(hdate, crop, y, month)
                buy = Future.objects.get_by_date(rdate, crop, y, month)
                net = float(sell.close) - float(buy.close)
                gross = float(mars.price) + net * q * 0.01
                quants[q] = gross
            except KeyError:
                continue
        if len(quants) == len(quantities):
            # only add this if all quantities were found
            df[y] = quants

    return df


def contract_plot(crop, location, hday, hmon, rday, rmon, quantity,
                  years=None, months=None):
    '''return list of hedge data points varying contract month

    @@@ because all 3 prices are needed to calculate 'gross' there
    can be a different number of 'gross' values per month.  this
    may lead to some anomalies.  this is noticable when quantity is
    zero.  in that case all results should be the same (because the
    computed gross only depends on the mars price); however, the values
    are often different.
    '''
    df = {}

    if not years:
        years = range(2010, 2020)

    if not months:
        months = range(1, 13)

    for m in months:
        vals = []
        for y in years:
            hdate = datetime.date(y, hmon, hday)
            rdate = datetime.date(y, rmon, rday)
            try:
                mars = Price.objects.get_by_date(rdate, crop, location)
                if rmon >= m:
                    y_ = y + 1
                else:
                    y_ = y
                sell = Future.objects.get_by_date(hdate, crop, y_, m)
                buy = Future.objects.get_by_date(rdate, crop, y_, m)
                net = float(sell.close) - float(buy.close)
                gross = float(mars.price) + quantity * 0.01 * net
                vals.append(gross)
            except KeyError:    # as e:
                continue
        if len(vals) > 0:
            df[m] = vals
    return df


def recon_dates_plot(crop, location, hday, hmon, rday, rmonths, quantity,
                     month, years=None):
    '''return list of hedge data points varying by recon date'''
    df = {}

    if not years:
        years = range(2010, 2020)

    for rmon in rmonths:
        vals = []
        for y in years:
            hdate = datetime.date(y, hmon, hday)
            rdate = datetime.date(y, rmon, rday)
            try:
                mars = Price.objects.get_by_date(rdate, crop, location)
                if rmon >= month:
                    y_ = y + 1
                else:
                    y_ = y
                sell = Future.objects.get_by_date(hdate, crop, y_, month)
                buy = Future.objects.get_by_date(rdate, crop, y_, month)
                net = float(sell.close) - float(buy.close)
                gross = float(mars.price) + quantity * 0.01 * net
                vals.append(gross)
            except KeyError:
                continue
        if len(vals) > 0:
            df[rmon] = vals
    return df


def stats(L):
    '''given list of values calcuate stats'''
    if len(L) < 2:
        val = L[0] if len(L) == 1 else 0.0
        return dict(
            mean=val,
            min=val,
            max=val,
            q1=val,
            med=val,
            q3=val,
        )

    quarts = statistics.quantiles(L)
    return dict(
        mean=statistics.mean(L),
        min=min(L),
        max=max(L),
        q1=quarts[0],
        med=quarts[1],
        q3=quarts[2],
    )
