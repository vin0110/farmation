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
from .forms import (
    StateYearForm,
    StateCropForm,
)


def _number_fmt(amt, scale=1):
    if 0 < amt < scale:
        return "{:0.3f}".format(amt/scale)
    else:
        return "{:,}".format(round(amt/scale))


THIS_YEAR = 2020


def _mk_commodities(data, sub_cols):
    ncols = len(sub_cols)
    fmt = "|".join(['%s'] * (ncols + 1))
    mk_key = lambda row: fmt %\
        tuple([row['commodity_desc']] + [row[a[1]] for a in sub_cols])

    # need to transpose the data; rows are crop, columns are year
    commodities = {}
    for row in data:
        key = mk_key(row)
        thisyear = row['year']
        if key not in commodities:
            commodities[key] = {}
        commodities[key][thisyear] = row['value']

    return commodities


def _mk_rows(commodities, years):
    # convert to array
    rows = []
    for key, value in commodities.items():
        this_row = key.split('|')
        for year in years:
            try:
                this_row.append("$"+_number_fmt(value[year], scale=1000))
            except KeyError:
                this_row.append("--")
        rows.append(this_row)

    return rows


def _production_totals(request, query, query_dict):
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
            operation = query_dict['operation']
            response = esp_call(operation,
                                group=query.upper(), state=state, year=year)
            try:
                op = operation + "Response"
                data = response[op]['Results']['Result 1']['Row']
            except KeyError:
                messages.warning(request, 'Connect to data server failed')
                data = {}

            for i in range(len(data)):
                for k in data[i].keys():
                    val = data[i][k]
                    if isinstance(val, str):
                        val = val.strip().capitalize()
                        data[i][k] = val

            commodities = _mk_commodities(data, query_dict['sub_cols'])
            years = list(range(year-4, year+1))
            rows = _mk_rows(commodities, years)
            print('r', rows[0])
            print('y', years)

            year_earlier = year - 5
            year_later = year + 5 if year < THIS_YEAR else None
            columns = [{}] * (len(query_dict['sub_cols']) + 1)\
                + [{'className': "text-right"}] * len(years)
    else:
        form = theform()
        data = {}
        years = []
        rows = []
        year = ''
        state = ''
        year_earlier = None
        year_later = None
        columns = []

    years = list(set(years))
    years.sort()
    context = dict(form=form, years=years, year=year, state=state,
                   year_earlier=year_earlier, year_later=year_later,
                   sub_cols=query_dict['sub_cols'],
                   columns=json.dumps(columns),
                   title=title, rows=json.dumps(rows))
    return HttpResponse(render(request, template_name, context))


CROP_DICT = {
    'sub_cols': [('Class', 'class_desc'), ],
    'operation': 'production-total',
}
ANIMAL_DICT = {
    'sub_cols': [('Class', 'class_desc'), ],
    'operation': 'animal-production-total',
}
COUNTY_DICT = {
    'sub_cols': [('Class', 'class_desc'),
                 ('County', 'county_name'),
                 ('Practice', 'util_practice_desc'), ],
    'operation': 'production-total-county',
}


def field_crop_totals(request):
    return _production_totals(request, 'field crops', CROP_DICT)


def vegetable_totals(request):
    return _production_totals(request, 'vegetables', CROP_DICT)


def fruit_tree_totals(request):
    return _production_totals(request, 'fruit & tree nuts', CROP_DICT)


def horticulture_totals(request):
    return _production_totals(request, 'horticulture', CROP_DICT)


def crop_totals(request):
    return _production_totals(request, 'crop totals', CROP_DICT)


def livestock_totals(request):
    return _production_totals(request, 'livestock', ANIMAL_DICT)


def poultry_totals(request):
    return _production_totals(request, 'poultry', ANIMAL_DICT)


def dairy_totals(request):
    return _production_totals(request, 'dairy', ANIMAL_DICT)


def aquaculture_totals(request):
    return _production_totals(request, 'aquaculture', ANIMAL_DICT)


def specialty_totals(request):
    return _production_totals(request, 'specialty', ANIMAL_DICT)


def county_production_totals(request):
    return _production_totals(request, 'field crops', COUNTY_DICT)


def area_planted_harvested(request):
    template_name = 'viewer/area_planted_harvested.html'
    operation = "planted_harvested_by_state"
    theform = StateCropForm

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state'].upper()
            crop = form.cleaned_data['crop'].capitalize()

            response = esp_call(operation, state=state, crop=crop.upper())
            try:
                op = operation + "Response"
                data = response[op]['Results']['Result 1']['Row']
                rows = []
                for item in data:
                    row = [
                        item['year'],
                        _number_fmt(item['acres_planted']),
                        _number_fmt(item['acres_harvested']),
                        "{:3d}%".format(int(
                            item['acres_harvested']/item['acres_planted']*100)),
                    ]
                    rows.append(row)
            except KeyError:
                messages.warning(request, 'Connect to data server failed')
                data = {}
    else:
        data = {}
        form = theform()
        state = ''
        crop = ''

    context = dict(form=form, state=state, crop=crop, rows=rows)
    return HttpResponse(render(request, template_name, context))
