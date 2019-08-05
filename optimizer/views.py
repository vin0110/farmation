from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.decorators import login_required

from .models import (Scenario,
                     Crop,
                     )
from farm.models import Farm, CropData

from .forms import (ScenarioEditForm,
                    CropAcresSetForm,
                    AddMultipleCropForm,
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
    crops = farm.getCrops()
    for crop_name in crops:
        Crop.objects.create(
            name=crop_name,
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
    '''edit a crop'''
    template_name = 'optimizer/crop_details.html'
    theform = CropAcresSetForm

    crop = get_object_or_404(Crop, pk=pk)
    crop = get_object_or_404(Crop, pk=pk)
    if crop.scenario.farm.user != request.user:
        raise Http404

    context = dict(crop=crop, )

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            low = form.cleaned_data['low']
            high = form.cleaned_data['high']
            acreage = crop.scenario.farm.acreage()
            if low > acreage or high > acreage:
                # @@@ need to actually check if acres > farm - sum(other crops)
                messages.error(request, 'Limit is greater than farm')
            else:
                crop.lo_acres = low
                crop.hi_acres = high
                crop.save()
                return HttpResponseRedirect(
                    reverse('optimizer:crop_details', args=(crop.id, )))
    else:
        # method === GET
        form = theform(initial={'low': crop.lo_acres,
                                'high': crop.hi_acres, })

    context = dict(crop=crop, form=form, )
    return render(request, template_name, context)
    return HttpResponse(render(request, template_name, context))


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
    form = AddMultipleCropForm

    scenario = get_object_or_404(Scenario, pk=pk)
    if scenario.farm.user != request.user:
        raise Http404

    possible_crops = []
    farm_crops = scenario.farm.getCrops()
    for crop in farm_crops:
        try:
            scenario.crops.get(name=crop)
            # crop is in the list; it is not possible
        except Crop.DoesNotExist:
            possible_crops.append((crop, crop))

    if request.method == "POST":
        theform = form(request.POST)
        theform.fields['crops'].choices = possible_crops
        if theform.is_valid():
            selected_crops = theform.cleaned_data['crops']
            for new_crop in selected_crops:
                crop = Crop.objects.create(name=new_crop, scenario=scenario)
                scenario.crops.add(crop)
            return HttpResponseRedirect(
                reverse('optimizer:scenario_details', args=(scenario.id, )))
    else:
        # GET or invalid form
        theform = form()

    if len(possible_crops) == 0:
        if len(farm_crops) < CropData.objects.count():
            msg = "All crops allowed in this farm have been added. "\
                  "Must reconfigure farm to add more crops."
        else:
            msg = 'All crops have been added to this scenario.'
        messages.info(request, msg)
        return HttpResponseRedirect(
            reverse('optimizer:scenario_details', args=(scenario.id, )))

    theform.fields['crops'].choices = possible_crops

    context = dict(scenario=scenario, form=theform)
    return render(request, template_name, context)


@login_required
def analyze(request, pk):
    '''analyze scenario'''
    scenario = get_object_or_404(Scenario, pk=pk, farm__user=request.user)

    scenario.analyzeScenario()
    messages.info(request,
                  'Analyzed scenario "{}"'.format(scenario))

    return HttpResponseRedirect(
        request.META.get(
            'HTTP_REFERER',
            reverse('optimizer:scenario_details', args=(scenario.id, ))))
