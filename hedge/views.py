import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import (
    Location,
)

from .plots import (
    quantity_plot,
    contract_plot,
    stats,
)
from .forms import (
    QuantityForm,
    ContractForm,
)


def quantity_plot_form(request):
    '''parses the form and redirects to quantity plot'''
    pass


def quantity(request):
    template_name = 'hedge/quantity_plot.html'
    theform = QuantityForm

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            crop = form.cleaned_data['crop']
            loc = form.cleaned_data['location']
            hmon = int(form.cleaned_data['hedge_month'])
            hday = form.cleaned_data['hedge_day']
            rmon = int(form.cleaned_data['reconciliation_month'])
            rday = form.cleaned_data['reconciliation_day']
            month = form.cleaned_data['contract_month']
            data = quantity_plot(crop, loc, hday, hmon, rday, rmon, month)
            df = []
            if data:
                for year in data:
                    for q in data[year]:
                        df.append(dict(year=year,
                                       quantity=q,
                                       gross=data[year][q]))
                note = ''
            else:
                note = 'no data'

            context = dict(
                df=json.dumps(df),
                data=data,
                hdate=f'{hmon:02d}-{hday:02d}',
                rdate=f'{rmon:02d}-{rday:02d}',
                location=loc,
                crop=crop,
                month=month,
                form=form,
                note=note,
            )
            return HttpResponse(render(request, template_name, context))
    else:
        form = theform()

    context = dict(form=form)
    return HttpResponse(render(request, template_name, context))


def contract(request):
    template_name = 'hedge/contract_plot.html'
    theform = ContractForm

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            crop = form.cleaned_data['crop']
            loc = form.cleaned_data['location']
            hmon = int(form.cleaned_data['hedge_month'])
            hday = form.cleaned_data['hedge_day']
            rmon = int(form.cleaned_data['reconciliation_month'])
            rday = form.cleaned_data['reconciliation_day']
            quantity = form.cleaned_data['quantity']

            data = contract_plot(crop, loc, hday, hmon, rday, rmon, quantity)
            df = []
            if data:
                for month in data:
                    d = stats(data[month])
                    d['month'] = month
                    df.append(d)
                note = ''
            else:
                note = 'no data'

            context = dict(
                df=json.dumps(df),
                data=df,
                hdate=f'{hmon:02d}-{hday:02d}',
                rdate=f'{rmon:02d}-{rday:02d}',
                location=loc,
                crop=crop,
                form=form,
                note=note,
            )
            return HttpResponse(render(request, template_name, context))
    else:
        form = theform()

    context = dict(form=form)
    return HttpResponse(render(request, template_name, context))
