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


def _mk_commodities(data, sub_cols):
    ncols = len(sub_cols)
    if ncols == 1:
        mk_key = lambda row: "%s|%s" % (
            row['commodity_desc'], row[sub_cols[0][1]])
    elif ncols == 2:
        mk_key = lambda row: "%s|%s|%s" % (
            row['commodity_desc'], row[sub_cols[0][1]], row[sub_cols[1][1]])
    else:
        assert False, 'hmm'

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
                this_row.append(_dollar_fmt(value[year]))
            except KeyError:
                this_row.append("--")
        rows.append(this_row)

    return rows


def _production_totals(request, query, query_dict):
    '''returns production in dollars aggregated by state'''
    template_name = "viewer/production-total.html"
    theform = StateYearForm

    title = query.capitalize()

    print('q', query_dict)

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state'].upper()
            try:
                year = int(form.cleaned_data['year'])
            except ValueError:
                year = THIS_YEAR
            print("Y", year)
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

            print("D", len(data))
            commodities = _mk_commodities(data, query_dict['sub_cols'])
            print("C", len(commodities))
            years = list(range(year-4, year+1))
            rows = _mk_rows(commodities, years)
            print("R", len(rows))

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
                   sub_cols=query_dict['sub_cols'],
                   title=title, rows=json.dumps(rows))
    return HttpResponse(render(request, template_name, context))


CROP_DICT = {
    'sub_cols': [('Class', 'class_desc'), ],
    'operation': 'production-total',
}
ANIMAL__DICT = {
    'sub_cols': [('Class', 'class_desc'), ('Group', 'group_desc'), ],
    'operation': 'animal-production-total',
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


# animal products
def _animal_production_totals(request, query):
    '''returns production in dollars aggregated by state'''
    template_name = "viewer/animal-production-total.html"
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
            response = esp_call('animal-production-total',
                                group=query.upper(), state=state, year=year)
            try:
                data = response["animal-production-totalResponse"]['Results']['Result 1']['Row']
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
                key = "%s,%s,%s" % (row['commodity_desc'],
                                    row['class_desc'],
                                    row['group_desc'])
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
