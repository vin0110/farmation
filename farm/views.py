from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from farm.models import (Farm,
                         CropData, )
from optimizer.forms import AddMultipleCropForm


@login_required
def home(request):
    '''the overall home view'''
    template_name = "home.html"

    farms = Farm.objects.filter(user=request.user)
    cnt = farms.count()
    if cnt == 0:
        farm = Farm.create1KFarm(request.user)
    elif cnt > 1:
        raise Http404
    else:
        farm = farms[0]

    context = dict(
        farm=farm,
    )
    return HttpResponse(render(request, template_name, context))


@login_required
def farm(request, pk):
    '''display the specifics of the farm'''

    template_name = 'farm/farm.html'

    farm = get_object_or_404(Farm, pk=pk, user=request.user)
    context = dict(farm=farm, )
    return HttpResponse(render(request, template_name, context))


@login_required
def removeCropFromFarm(request, pk, crop):
    '''remove crop from a farm'''
    farm = get_object_or_404(Farm, pk=pk)
    if farm.user != request.user:
        raise Http404

    try:
        farm.rmCrop(crop)
        messages.info(request, 'Crop "{}" removed.'.format(crop))
    except ValueError:
        # failed to remove crop
        messages.warning(request, 'Could not remove crop "{}".'.format(crop))

    return HttpResponseRedirect(reverse('farm:farm', args=(farm.id, )))


@login_required
def addCropToFarm(request, pk):
    '''select crop from form and add to farm
    determine possible crops'''
    template_name = 'farm/add_crop_to_farm.html'
    form = AddMultipleCropForm

    farm = get_object_or_404(Farm, pk=pk)
    if farm.user != request.user:
        raise Http404

    possible_crops = []
    farm_crops = farm.getCrops()
    for crop in CropData.objects.all():
        if crop.name not in farm_crops:
            possible_crops.append((crop.name, crop.name))

    if request.method == "POST":
        theform = form(request.POST)
        theform.fields['crops'].choices = possible_crops

        if theform.is_valid():
            selected_crops = theform.cleaned_data['crops']
            for new_crop in selected_crops:
                try:
                    farm.addCrop(new_crop)
                except ValueError as e:
                    messages.warning(request, e)
            return HttpResponseRedirect(
                reverse('farm:farm', args=(farm.id, )))
    else:
        # GET or invalid form
        theform = form()

    if len(possible_crops) == 0:
        if len(farm_crops) < CropData.objects.count():
            messages.info(request,
                          "All known crops have been added to this farm.")
        return HttpResponseRedirect(
            reverse('farm:farm', args=(farm.id, )))

    theform.fields['crops'].choices = possible_crops

    context = dict(farm=farm, form=theform)
    return render(request, template_name, context)
