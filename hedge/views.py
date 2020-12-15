import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import (
    Location,
)

from .plots import quantity_plot


def quantity(request, loc, hday, hmon, rday, rmon, month):
    template_name = 'hedge/quantity_plot.html'

    loc = get_object_or_404(Location, pk=loc)
    data = quantity_plot("C", loc, hday, hmon, rday, rmon, month)

    df = []
    for year in data:
        for q in data[year]:
            df.append(dict(year=year, quantity=q, gross=data[year][q]))

    context = dict(
        df=json.dumps(df),
        data=data,
        hdate=f'{hmon:02d}-{hday:02d}',
        rdate=f'{rmon:02d}-{rday:02d}',
        location=loc,
        crop="corn",
        month=month,
    )

    return HttpResponse(render(request, template_name, context))
