import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .models import (
    Location,
    CROP_DICT,
)

from .plots import (
    quantity_plot,
    contract_plot,
    recon_dates_plot,
    stats,
)
from .forms import (
    QuantityForm,
    ContractForm,
    ReconForm,
    CropForm,
    LocationForm,
)


def quantity_plot_form(request):
    '''parses the form and redirects to quantity plot'''
    pass


def get_mon_day(text):
    mon = int(text[0:2])
    day = int(text[3:5])
    return (mon, day)


def quantity(request, crop, lid):
    template_name = 'hedge/quantity_plot.html'
    theform = QuantityForm

    if crop not in CROP_DICT.values():
        raise Http404
    location = get_object_or_404(Location, id=lid)

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            hedge_date = form.cleaned_data['hedge_date']
            reconcilliation_date = form.cleaned_data['reconcilliation_date']
            month = form.cleaned_data['contract_month']

            try:
                hmon, hday = get_mon_day(hedge_date)
                rmon, rday = get_mon_day(reconcilliation_date)

                data = quantity_plot(
                    crop, location, hday, hmon, rday, rmon, month)

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
                    crop=crop,
                    location=location,
                    df=json.dumps(df),
                    data=data,
                    form=form,
                    note=note,
                )
                return HttpResponse(render(request, template_name, context))
            except ValueError:
                messages.error(request, "Invalid date")
    else:
        form = theform(initial=dict(crop=crop, location=location))

    context = dict(form=form, crop=crop, location=location)
    return HttpResponse(render(request, template_name, context))


def contract(request, crop, lid):
    template_name = 'hedge/contract_plot.html'
    theform = ContractForm

    if crop not in CROP_DICT.values():
        raise Http404
    location = get_object_or_404(Location, id=lid)

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            hedge_date = form.cleaned_data['hedge_date']
            reconcilliation_date = form.cleaned_data['reconcilliation_date']
            quantity = form.cleaned_data['quantity']

            try:
                hmon, hday = get_mon_day(hedge_date)
                rmon, rday = get_mon_day(reconcilliation_date)

                data = contract_plot(
                    crop, location, hday, hmon, rday, rmon, quantity)
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
                    crop=crop,
                    location=location,
                    df=json.dumps(df),
                    data=df,
                    form=form,
                    note=note,
                )
                return HttpResponse(render(request, template_name, context))
            except ValueError:
                messages.error(request, "Invalid date")
    else:
        form = theform()

    context = dict(form=form, crop=crop, location=location)
    return HttpResponse(render(request, template_name, context))


def recon(request, crop, lid):
    template_name = 'hedge/recon_dates_plot.html'
    theform = ReconForm

    if crop not in CROP_DICT.values():
        raise Http404
    location = get_object_or_404(Location, id=lid)

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            hedge_date = form.cleaned_data['hedge_date']
            rday = form.cleaned_data['reconcilliation_day']
            quantity = form.cleaned_data['quantity']
            month = int(form.cleaned_data['contract_month'])
            rmonths = [int(m)
                       for m in form.cleaned_data['reconciliation_months']]

            try:
                hmon, hday = get_mon_day(hedge_date)

                data = recon_dates_plot(crop, location, hday, hmon, rday,
                                        rmonths, quantity, month)
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
                    crop=crop,
                    location=location,
                    df=json.dumps(df),
                    data=df,
                    form=form,
                    note=note,
                )
                return HttpResponse(render(request, template_name, context))
            except ValueError:
                messages.error(request, "Invalid date")
    else:
        form = theform()

    context = dict(form=form, crop=crop, location=location)
    return HttpResponse(render(request, template_name, context))


# wizard views
def wizard(request):
    template_name = 'hedge/wizard.html'
    theform = CropForm

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            crop_index = form.cleaned_data['crop']
            crop = CROP_DICT[crop_index]
            return HttpResponseRedirect(
                reverse('hedge:wizard_crop', args=(crop, )))
    else:
        form = theform()

    context = dict(form=form)
    return HttpResponse(render(request, template_name, context))


def wizard_crop(request, crop):
    '''the crop has been selected'''
    template_name = 'hedge/wizard_crop.html'
    theform = LocationForm

    if crop not in CROP_DICT.values():
        raise Http404

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            location = form.cleaned_data['location']

            return HttpResponseRedirect(
                reverse('hedge:select', args=(crop, location.id)))
    else:
        form = theform()

    context = dict(form=form, crop=crop)
    return HttpResponse(render(request, template_name, context))


def wizard_select(request, crop, lid):
    template_name = 'hedge/wizard_select.html'

    print('s', crop, lid)

    if crop not in CROP_DICT.values():
        print('here')
        raise Http404
    location = get_object_or_404(Location, id=lid)

    return HttpResponse(
        render(request, template_name, dict(crop=crop, location=location)))
