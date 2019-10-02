from math import sqrt
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.decorators import login_required

from .models import (Scenario,
                     Crop,
                     CropData,
                     PriceOrder,
                     )
from farm.models import Farm

from .forms import (ScenarioEditForm,
                    CropAcresSetForm,
                    AddMultipleCropForm,
                    CropForm,
                    EditYieldForm,
                    PriceOrderForm,
                    )


@login_required
def scenarioList(request, pk):
    '''dashboard for optimizer'''
    template_name = "optimizer/list.html"

    farm = get_object_or_404(Farm, pk=pk, user=request.user)

    context = dict(
        farm=farm,
    )

    return HttpResponse(render(request, template_name, context))


@login_required
def scenarioAdd(request, pk):
    '''create a new scenario'''
    def number2words(n):
        name = []
        while n > 0:
            name.append(
                ['zero', 'one', 'two', 'three', 'four',
                 'five', 'six', 'seven', 'eight', 'nine'][n % 10])
            n //= 10
        return '-'.join(name)

    farm = get_object_or_404(Farm, pk=pk, user=request.user)
    cnt = Scenario.objects.filter(farm=farm).count()
    name = number2words(cnt+1)
    scenario = Scenario.objects.create(
        farm=farm,
        name=name,
    )
    crops = farm.crops.all()
    for crop in crops:
        Crop.objects.create(
            data=crop.data,
            farmcrop=crop,
            scenario=scenario, )

    return HttpResponseRedirect(
        reverse('optimizer:scenario_details', args=(scenario.id, )))


@login_required
def scenarioDetails(request, pk):
    '''edit a scenario'''
    template_name = 'optimizer/scenario_details.html'
    theform = ScenarioEditForm

    scenario = get_object_or_404(Scenario, pk=pk, farm__user=request.user)

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            scenario.name = name
            scenario.save()
    else:
        # GET
        form = theform(instance=scenario)

    context = dict(scenario=scenario,
                   form=ScenarioEditForm(),)

    return HttpResponse(render(request, template_name, context))


@login_required
def cropDetails(request, pk):
    '''display a crop'''
    template_name = 'optimizer/crop_details.html'

    cropdata = get_object_or_404(CropData, pk=pk)
    context = dict(cropdata=cropdata, )
    return render(request, template_name, context)


@login_required
def removeCropFromScenario(request, pk):
    '''remove crop from a scenario'''
    crop = get_object_or_404(Crop, pk=pk)
    scenario = crop.scenario
    if scenario.farm.user != request.user:
        raise Http404

    crop.delete()
    return HttpResponseRedirect(
        reverse('optimizer:scenario_details', args=(scenario.id, )))


@login_required
def addCropToScenario(request, pk):
    '''select crop from form and add to scenario
    determine possible crops'''
    template_name = 'optimizer/add_crop_to_scenario.html'
    theform = AddMultipleCropForm

    scenario = get_object_or_404(Scenario, pk=pk)
    if scenario.farm.user != request.user:
        raise Http404

    possible_crops = []
    farm_crops = scenario.farm.crops.all()
    for crop in farm_crops:
        try:
            scenario.crops.get(data=crop.data)
            # crop is in the list; it is not possible
        except Crop.DoesNotExist:
            possible_crops.append((crop.data.name, crop.data.name))

    if request.method == "POST":
        form = theform(request.POST)
        form.fields['crops'].choices = possible_crops
        if form.is_valid():
            selected_crops = form.cleaned_data['crops']
            for new_crop in selected_crops:
                data = CropData.objects.get(name=new_crop)
                crop = Crop.objects.create(
                    data=data,
                    farmcrop=farm_crops.get(data=data),
                    scenario=scenario)
                scenario.crops.add(crop)
            return HttpResponseRedirect(
                reverse('optimizer:scenario_details', args=(scenario.id, )))
    else:
        # GET or invalid form
        form = theform()

    if len(possible_crops) == 0:
        if scenario.farm.crops.count() < CropData.objects.count():
            msg = "All crops allowed in this farm have been added. "\
                  "Must reconfigure farm to add more crops."
        else:
            msg = 'All crops have been added to this scenario.'
        messages.info(request, msg)
        return HttpResponseRedirect(
            reverse('optimizer:scenario_details', args=(scenario.id, )))

    form.fields['crops'].choices = possible_crops

    context = dict(scenario=scenario, form=form)
    return render(request, template_name, context)


@login_required
def analyze(request, pk):
    '''analyze scenario'''
    scenario = get_object_or_404(Scenario, pk=pk, farm__user=request.user)

    try:
        scenario.analyzeScenario()
        messages.info(request,
                      'Analyzed scenario "{}"'.format(scenario))
    except ValueError as e:
        messages.error(request, e)

    return HttpResponseRedirect(
        request.META.get(
            'HTTP_REFERER',
            reverse('optimizer:scenario_details', args=(scenario.id, ))))


@login_required
def editCrop(request, pk):
    '''edit the overrides in crop'''
    template_name = 'optimizer/edit_crop.html'
    form = CropForm

    crop = get_object_or_404(Crop, pk=pk)
    scenario = crop.scenario

    if request.method == "POST":
        theform = form(request.POST, instance=crop)
        if theform.is_valid():
            valid = True
            farmcrop = scenario.farm.crops.get(data=crop.data)
            lo = theform.cleaned_data['lo_acres']
            hi = theform.cleaned_data['hi_acres']
            flo = farmcrop.lo_acres
            fhi = farmcrop.hi_acres
            if lo > 0:
                if lo < flo:
                    messages.error(
                        request,
                        'cannot set low limit to less than the '
                        'farm low limit of {}'.format(flo))
                    valid = False
                if fhi > 0 and lo > fhi:
                    messages.error(
                        request,
                        'cannot set low limit to greater than the '
                        'farm low limit of {}'.format(fhi))
                    valid = False
            if hi > 0:
                if fhi > 0 and hi > fhi:
                    messages.error(
                        request,
                        'cannot set high limit to greater than the '
                        'farm high limit of {}'.format(fhi))
                    valid = False
                if flo > 0 and hi < flo:
                    messages.error(
                        request,
                        'cannot set high limit to less than the '
                        'farm low limit of {}'.format(flo))
                    valid = False
            if hi > 0 and lo > hi:
                messages.error(
                    request,
                    'low limit ({}) is greater than high ({})'.format(lo, hi))
                valid = False
            if valid:
                theform.save()
                return HttpResponseRedirect(
                    reverse('optimizer:scenario_details',
                            args=(scenario.id, )))
    else:
        # GET
        theform = form(instance=crop)

    context = dict(crop=crop, form=theform)
    return render(request, template_name, context)


@login_required
def editYieldOverride(request, pk, clear=False):
    '''edit a yield override'''
    template_name = 'optimizer/yield_override.html'
    theform = EditYieldForm

    crop = get_object_or_404(Crop, pk=pk)

    if crop.scenario.farm.user != request.user:
        raise Http404

    if clear:
        crop.yield_override = ''
        crop.save()
        return HttpResponseRedirect(
            reverse('optimizer:scenario_details',
                    args=(crop.scenario.id, )))

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            low = form.cleaned_data['low']
            peak = form.cleaned_data['peak']
            high = form.cleaned_data['high']
            crop.yield_override = json.dumps([low, peak, high])
            crop.save()
            return HttpResponseRedirect(
                reverse('optimizer:scenario_details',
                        args=(crop.scenario.id, )))
    else:
        # method === GET
        if crop.isYieldOverride():
            low, peak, high = json.loads(crop.yield_override)
        else:
            low, peak, high = json.loads(crop.data.yields)
        form = theform(initial=dict(low=low, peak=peak, high=high))

    context = dict(crop=crop, form=form)
    return render(request, template_name, context)


@login_required
def addPrice(request, pk):
    '''add price override for a crop; then call edit'''
    crop = get_object_or_404(Crop, pk=pk)
    if crop.scenario.farm.user != request.user:
        raise Http404
    price = PriceOrder.objects.create(crop=crop)

    return HttpResponseRedirect(
        reverse('optimizer:edit_price', args=(price.id, )))


@login_required
def editPrice(request, pk):
    '''edit the price override'''
    template_name = 'optimizer/edit_price.html'
    form = PriceOrderForm

    price = get_object_or_404(PriceOrder, pk=pk)
    scenario = price.crop.scenario

    if request.method == "POST":
        theform = form(request.POST, instance=price)
        if theform.is_valid():
            safety = int(theform.cleaned_data['safety'])
            lo, peak, hi = json.loads(price.crop.data.yields)
            # determine the percentile
            hgt = 100. / (hi - lo)
            a1 = (peak - lo) * hgt  # area of left tri (lo to peak)
            if safety <= a1:
                # a1 is percent of area in the left triangle
                # if safety is less than this area, price factor is
                # less than peak
                f = lo + sqrt((safety/a1) * (peak - lo)**2)
            else:
                # safety > a1, calculate factor subtracting from hi
                f = hi - sqrt((100. - safety)/(100. - a1) * (hi - peak)**2)
            price.factor = f
            theform.save()
            return HttpResponseRedirect(
                reverse('optimizer:scenario_details',
                        args=(scenario.id, )))
    else:
        # GET
        theform = form(instance=price)

    context = dict(price=price, form=theform)
    return render(request, template_name, context)


@login_required
def removePrice(request, pk):
    '''remove price from crop'''
    price = get_object_or_404(PriceOrder, pk=pk)
    scenario = price.crop.scenario
    if scenario.farm.user != request.user:
        raise Http404

    price.delete()
    return HttpResponseRedirect(
        reverse('optimizer:scenario_details', args=(scenario.id, )))


@login_required
def updateScenario(request, pk):
    '''update scenario analysis'''
    scenario = get_object_or_404(Scenario, pk=pk)
    if scenario.farm.user != request.user:
        raise Http404
    scenario.analyzeScenario()
    return HttpResponseRedirect(
        reverse('optimizer:scenario_details', args=(pk, )))
