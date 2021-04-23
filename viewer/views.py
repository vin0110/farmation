import json

# from django.urls import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
# from django.shortcuts import get_object_or_404
# from django.views.generic.list import ListView
# from django.views.generic.detail import DetailView
# from django.views.generic.edit import UpdateView
# from braces.views import LoginRequiredMixin

from .utils import esp_call
from .forms import StateYearForm


def _dollar_fmt(amt, scale=1000):
    if 0 < amt < 1000:
        return "${:0.3f}".format(amt/scale)
    else:
        return "${:,}".format(round(amt/scale))

THIS_YEAR = 2020

def _production_totals(request, query):
    '''returns production in dollars aggregated by state'''
    template_name = "viewer/production-total.html"
    theform = StateYearForm

    title = query.capitalize()

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state'].upper()
            try:
                year = int(form.cleaned_data['year'])
            except ValueError:
                year = THIS_YEAR
            print("Y", year)
            response = esp_call('production-total',
                                group=query.upper(), state=state, year=year)
            try:
                data = response["production-totalResponse"]['Results']['Result 1']['Row']
            except KeyError:
                messages.warning(request, 'Connect to data server failed')
                data = {}

            for i in range(len(data)):
                for k in data[i].keys():
                    val = data[i][k]
                    if isinstance(val, str):
                        val = val.strip().capitalize()
                        data[i][k] = val

            # print(data)

            # need to transpose the data; rows are crop, columns are year
            commodities = {}
            for row in data:
                key = "%s,%s" % (row['commodity_desc'], row['class_desc'])
                thisyear = row['year']
                if key not in commodities:
                    commodities[key] = {}
                commodities[key][thisyear] = row['value']

            # convert to array
            rows = []
            years = list(range(year-4, year+1))
            print("YY", years)
            for key, value in commodities.items():
                this_row = key.split(',', 1)  # make two cols out of key
                for year in years:
                    try:
                        this_row.append(_dollar_fmt(value[year]))
                    except KeyError:
                        this_row.append("--")
                rows.append(this_row)

            year_earlier = year - 5
            year_later = year + 5 if year < THIS_YEAR else None
    else:
        form = theform()
        data = {}
        years = []
        rows = []
        year = ''
        state = ''
        year_earlier = None
        year_later = None

    years = list(set(years))
    years.sort()
    context = dict(form=form, years=years, year=year, state=state,
                   year_earlier=year_earlier, year_later=year_later,
                   title=title, rows=json.dumps(rows))
    return HttpResponse(render(request, template_name, context))


def field_crop_totals(request):
    return _production_totals(request, 'field crops')


def vegetable_totals(request):
    return _production_totals(request, 'vegetables')


def fruit_tree_totals(request):
    return _production_totals(request, 'fruit & tree nuts')


def horticulture_totals(request):
    return _production_totals(request, 'horticulture')


def crop_totals(request):
    return _production_totals(request, 'crop totals')


def _quantity_totals(request, query):
    '''return production in quantity (ie, bu) by state'''
    template_name = "viewer/quantity-total.html"
    theform = StateYearForm

    title = query.capitalize()

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state'].upper()
            try:
                year = int(form.cleaned_data['year'])
            except ValueError:
                year = 2019
            print("Y", year)
            response = esp_call('production-total',
                                group=query.upper(), state=state, year=year)
            try:
                data = response["production-totalResponse"]['Results']['Result 1']['Row']
            except KeyError:
                messages.warning(request, 'Connect to data server failed')
                data = {}

            for i in range(len(data)):
                for k in data[i].keys():
                    val = data[i][k]
                    if isinstance(val, str):
                        val = val.strip().capitalize()
                        data[i][k] = val

            # print(data)

            # need to transpose the data; rows are crop, columns are year
            commodities = {}
            for row in data:
                key = "%s,%s" % (row['commodity_desc'], row['class_desc'])
                thisyear = row['year']
                if key not in commodities:
                    commodities[key] = {}
                commodities[key][thisyear] = row['value']

            # convert to array
            rows = []
            years = list(range(year-4, year+1))
            print("YY", years)
            for key, value in commodities.items():
                this_row = key.split(',', 1)  # make two cols out of key
                for year in years:
                    try:
                        this_row.append(_dollar_fmt(value[year]))
                    except KeyError:
                        this_row.append("--")
                rows.append(this_row)
    else:
        form = theform()
        data = {}
        years = []
        rows = []
        year = ''
        state = ''

    years = list(set(years))
    years.sort()
    context = dict(form=form, years=years, year=year, state=state,
                   title=title, rows=json.dumps(rows))
    return HttpResponse(render(request, template_name, context))
