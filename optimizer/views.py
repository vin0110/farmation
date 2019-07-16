from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404

from .models import (Scenario,
                     Crop,
                     )
from farm.models import Farm

from .forms import (ScenarioEditForm,
                    CropAddForm,
                    )


def scenarioList(request, pk):
    '''dashboard for optimizer'''
    template_name = "optimizer/home.html"

    farm = get_object_or_404(Farm, pk=pk, user=request.user)

    context = dict(
        farm=farm,
    )

    return HttpResponse(render(request, template_name, context))


def scenarioAdd(request, pk):
    '''create a new scenario'''
    farm = get_object_or_404(Farm, pk=pk, user=request.user)
    scenario = Scenario.objects.create(
        farm=farm,
    )
    crops = farm.getCrops()
    for crop_name in crops:
        Crop.objects.create(
            name=crop_name,
            scenario=scenario, )

    return HttpResponseRedirect(
        reverse('optimizer:scenario_details', args=(scenario.id, )))


def scenarioEdit(request, pk):
    '''edit a scenario'''
    template_name = 'optimizer/scenario_edit.html'
    theform = ScenarioEditForm

    scenario = get_object_or_404(Scenario, pk=pk, farm__user=request.user)

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            scenario.name = name
            scenario.save()
            return HttpResponseRedirect(reverse('optimizer:home'))
    else:
        # GET
        form = theform(instance=scenario)

    context = dict(scenario=scenario, form=form)
    return HttpResponse(render(request, template_name, context))


def scenarioDetails(request, pk):
    '''edit a scenario'''
    template_name = 'optimizer/scenario_details.html'

    scenario = get_object_or_404(Scenario, pk=pk, farm__user=request.user)
    context = dict(scenario=scenario)

    return HttpResponse(render(request, template_name, context))


def cropAdd(request, pk):
    '''add a crop to a scenario'''
    template_name = 'optimizer/crop_add.html'
    theform = CropAddForm

    scenario = get_object_or_404(Scenario, pk=pk, farm__user=request.user)

    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            Crop.objects.create(name=name)

            return HttpResponseRedirect(
                reverse('optimizer:scenario_details', args=(scenario.id)))
    else:
        # GET
        form = theform()

    context = dict(scenario=scenario, form=form)
    return HttpResponse(render(request, template_name, context))


def cropDetails(request, pk):
    '''edit a crop'''
    template_name = 'optimizer/crop_details.html'

    crop = get_object_or_404(Crop, pk=pk)
    context = dict(crop=crop, )

    return HttpResponse(render(request, template_name, context))


def analyze(request, pk):
    '''analyze scenario'''
    scenario = get_object_or_404(Scenario, pk=pk, farm__user=request.user)

    if scenario.state == "A":
        messages.info(request,
                      'Scenario "{}" already analyzed'.format(scenario))
    elif scenario.state == "M":
        for crop in scenario.crops.all():
            crop.analyze()
        scenario.analyzeScenario()
        messages.info(request,
                      'Analyzed scenario "{}"'.format(scenario))
    else:
        raise Http404
    return HttpResponseRedirect(
        request.META.get(
            'HTTP_REFERER',
            reverse('optimizer:scenario_details', args=(scenario.id, ))))
