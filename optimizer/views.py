from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import (Scenario,
                     Crop,
                     )
from farm.models import Farm

from .forms import (ScenarioEditForm,
                    CropAddForm,
                    )

def home(request):
    '''dashboard for optimizer'''
    template_name = "optimizer/home.html"

    farm = Farm.objects.first() # @@@ one farm
    context = dict(
        farm=farm,
    )
    
    return HttpResponse(render(request, template_name, context))

def scenarioAdd(request):
    '''add a scenario'''
    farm = Farm.objects.first() # @@@ one farm
    scenario = Scenario.objects.create(
        farm=farm,
    )
    
    return HttpResponseRedirect(
        reverse('optimizer:scenario_details', args=(scenario.id, )))


def scenarioEdit(request, pk):
    '''edit a scenario'''
    template_name = 'optimizer/scenario_edit.html'
    theform = ScenarioEditForm

    scenario = get_object_or_404(Scenario, pk=pk)
    
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

    scenario = get_object_or_404(Scenario, pk=pk)

    context = dict(scenario=scenario)

    return HttpResponse(render(request, template_name, context))
    
def cropAdd(request, pk):
    '''add a crop to a scenario'''
    template_name = 'optimizer/crop_add.html'
    theform = CropAddForm

    scenario = get_object_or_404(Scenario, pk=pk)
    
    if request.method == "POST":
        form = theform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            crop = Crop.objects.create(name=name)

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
    
