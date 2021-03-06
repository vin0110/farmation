import json

# from django.urls import reverse
from django.http import Http404, HttpResponse  # , HttpResponseRedirect
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
    CountyYearForm,
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


def _production_totals(request, state, query, query_dict):
    '''returns production in dollars aggregated by state'''
    template_name = "viewer/production-total.html"

    if state:
        by_county = True
        if len(state) != 2:
            raise Http404

        state = state.upper()
        theform = CountyYearForm

        # get list of counties (use sessions -- counties don't change much
        try:
            key = state + '_counties'
            counties = request.session[key]
        except KeyError:
            operation = 'list_counties'
            counties = []
            try:
                response = esp_call(operation, state=state)
                try:
                    op = operation + "Response"
                    data = response[op]['Results']['Result 1']['Row']
                    counties = []
                    for row in data:
                        raw_name = row['county_name'].strip()
                        name = raw_name.title()
                        counties.append((raw_name, name, ))
                        request.session[key] = counties
                except KeyError:
                    pass
            except ValueError as e:
                messages.warning(request, str(e))
            if len(counties) == 0:
                messages.warning(request, 'No county data')

    else:
        by_county = False
        theform = StateYearForm
        counties = []
        county = ''

    title = query.capitalize()

    if request.method == "POST":
        form = theform(request.POST)
        if by_county:
            form.fields['county'].choices = counties
        if form.is_valid():
            try:
                year = int(form.cleaned_data['year'])
            except ValueError:
                year = THIS_YEAR

            if by_county:
                county = form.cleaned_data['county'].upper()
                operation = query_dict['operation'] + '-county'
            else:
                state = form.cleaned_data['state'].upper()
                operation = query_dict['operation']

            try:
                data = {}
                response = esp_call(operation, state=state,
                                    group=query.upper(),
                                    county=county, year=year)
                try:
                    op = operation + "Response"
                    data = response[op]['Results']['Result 1']['Row']
                except KeyError:
                    messages.warning(request, 'Connect to data server failed')
            except ValueError as e:
                messages.warning(request, str(e))

            for i in range(len(data)):
                for k in data[i].keys():
                    val = data[i][k]
                    if isinstance(val, str):
                        val = val.strip().capitalize()
                        data[i][k] = val

            commodities = _mk_commodities(data, query_dict['sub_cols'])
            years = list(range(year-4, year+1))
            rows = _mk_rows(commodities, years)

            year_earlier = year - 5
            year_later = year + 5 if year < THIS_YEAR else None
            columns = [{}] * (len(query_dict['sub_cols']) + 1)\
                + [{'className': "text-right"}] * len(years)

    else:
        if by_county:
            form = theform(county_choices=counties)
        else:
            form = theform()

        data = {}
        years = []
        rows = []
        year = ''
        year_earlier = None
        year_later = None
        columns = []
        county = ''

    years = list(set(years))
    years.sort()
    context = dict(form=form, years=years, year=year, state=state,
                   year_earlier=year_earlier, year_later=year_later,
                   sub_cols=query_dict['sub_cols'],
                   columns=json.dumps(columns), county=county,
                   by_county=by_county,
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


def field_crop_totals(request, state=''):
    return _production_totals(request, state, 'field crops', CROP_DICT)


def vegetable_totals(request, state=''):
    return _production_totals(request, state, 'vegetables', CROP_DICT)


def fruit_tree_totals(request, state=''):
    return _production_totals(request, state, 'fruit & tree nuts', CROP_DICT)


def horticulture_totals(request, state=''):
    return _production_totals(request, state, 'horticulture', CROP_DICT)


def crop_totals(request, state=''):
    return _production_totals(request, state, 'crop totals', CROP_DICT)


def livestock_totals(request, state=''):
    return _production_totals(request, state, 'livestock', ANIMAL_DICT)


def poultry_totals(request, state=''):
    return _production_totals(request, state, 'poultry', ANIMAL_DICT)


def dairy_totals(request, state=''):
    return _production_totals(request, state, 'dairy', ANIMAL_DICT)


def aquaculture_totals(request, state=''):
    return _production_totals(request, state, 'aquaculture', ANIMAL_DICT)


def specialty_totals(request, state=''):
    return _production_totals(request, state, 'specialty', ANIMAL_DICT)


# def county_field_crop_totals(request, state):
#     return _production_totals(request, state, 'field crops', CROP_DICT)


# def county_vegetable_totals(request, state):
#     return _production_totals(request, state, 'vegetables', CROP_DICT)


# def county_fruit_tree_totals(request, state):
#     return _production_totals(request, state, 'fruit & tree nuts', CROP_DICT)


# def county_horticulture_totals(request, state):
#     return _production_totals(request, state, 'horticulture', CROP_DICT)


# def county_crop_totals(request, state):
#     return _production_totals(request, state, 'crop totals', CROP_DICT)


def area_planted_harvested_by_crop(request):
    template_name = 'viewer/area_planted_harvested.html'
    operation = "planted_harvested_by_state"
    theform = StateCropForm

    unit = ''

    if request.method == "POST":
        form = theform(request.POST)
        rows = []

        if form.is_valid():
            state = form.cleaned_data['state'].upper()
            crop = form.cleaned_data['crop']
            if crop == '':
                crop = 'corn'
            crop = crop.capitalize()

            try:
                response = esp_call(operation, state=state, crop=crop.upper())
                try:
                    op = operation + "Response"
                    data = response[op]['Results']['Result 1']['Row']
                except KeyError:
                    messages.warning(request,
                                     'Connect to data server failed: ')
            except ValueError as e:
                messages.warning(request, str(e))
                data = {}

            if data:
                for item in data:
                    row = [
                        item['year'],
                        _number_fmt(item['acres_planted']),
                        _number_fmt(item['acres_harvested']),
                        "{:3d}%".format(int(
                            item['acres_harvested']/item['acres_planted']*100)
                        ),
                        _number_fmt(item['yield']),
                        _number_fmt(item['acres_harvested'] * item['yield']),
                    ]
                    rows.append(row)
                unit = data[0]['unit_desc']
                unit = unit[:unit.find('/ ACRE')].strip()
        else:
            state = ''
            crop = ''
    else:
        rows = []
        form = theform()
        state = ''
        crop = ''

    context = dict(form=form, state=state, crop=crop, rows=rows, unit=unit)
    return HttpResponse(render(request, template_name, context))


def area_planted_harvested_by_year(request):
    template_name = 'viewer/area_planted_harvested_by_year.html'
    operation = "planted_harvested_by_year"
    theform = StateYearForm

    if request.method == "POST":
        form = theform(request.POST)
        rows = []
        if form.is_valid():
            state = form.cleaned_data['state'].upper()
            try:
                year = int(form.cleaned_data['year'])
            except ValueError:
                year = 2019

            try:
                response = esp_call(operation, state=state, year=year)
                try:
                    op = operation + "Response"
                    data = response[op]['Results']['Result 1']['Row']
                    totals = [0, 0]
                    for item in data:
                        row = [
                            item['commodity_desc'].capitalize(),
                            _number_fmt(item['acres_planted']),
                            _number_fmt(item['acres_harvested']),
                            "{:3d}%".format(int(
                                item['acres_harvested'] /
                                item['acres_planted']*100)
                            ),
                        ]
                        rows.append(row)
                        totals[0] += item['acres_planted']
                        totals[1] += item['acres_harvested']
                    years = [year-1 if year > 2000 else None,
                             year+1 if year < 2020 else None]
                    try:
                        totals.append("{:3d}%".format(
                            int(totals[1]/totals[0]*100)))
                    except ZeroDivisionError:
                        totals.append('')
                    totals[0] = _number_fmt(totals[0])
                    totals[1] = _number_fmt(totals[1])
                except KeyError:
                    messages.warning(request, 'Connect to data server failed')
            except ValueError as e:
                messages.warning(request, str(e))
    else:
        rows = []
        form = theform()
        state = ''
        year = ''
        years = [None, None]
        totals = ['0', '0', '']

    context = dict(form=form, state=state, year=year, rows=rows,
                   totals=totals, years=years)
    return HttpResponse(render(request, template_name, context))
