from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import (Farm, Field, )
from optimizer.models import CropData, FarmCrop
from optimizer.forms import AddMultipleCropForm, FarmCropForm


@login_required
def home(request):
    '''the overall home view'''
    def create1KFarm(user):
        '''create a 1000-acre farm'''
        farm = Farm(user=user,
                    name="Thousand-Acre Farm",)
        farm.save()
        for n in ['one', 'two', 'three', 'four', 'five',
                  'six', 'seven', 'eight', 'nine', 'ten']:
            Field.objects.create(
                farm=farm,
                name="Field {}".format(n),
                acreage=100)
        for crop_name in ['corn', 'soybeans', 'wheat']:
            crop_data = CropData.objects.get(name=crop_name)
            FarmCrop.objects.create(farm=farm, data=crop_data)
        return farm

    template_name = "home.html"

    farms = Farm.objects.filter(user=request.user)
    cnt = farms.count()
    if cnt == 0:
        # no farms; create default and reset queryset
        create1KFarm(request.user)
        farms = Farm.objects.filter(user=request.user)

    context = dict(
        farms=farms,
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
def removeCropFromFarm(request, pk):
    '''remove crop from a farm'''
    crop = get_object_or_404(FarmCrop, pk=pk)
    farm = crop.farm
    if farm.user != request.user:
        raise Http404

    try:
        crop.delete()
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
    for data in CropData.objects.all():
        try:
            farm.crops.get(data=data)
        except FarmCrop.DoesNotExist:
            possible_crops.append((data.name, data.name))

    if request.method == "POST":
        theform = form(request.POST)
        theform.fields['crops'].choices = possible_crops

        if theform.is_valid():
            selected_crops = theform.cleaned_data['crops']
            for new_crop in selected_crops:
                data = CropData.objects.get(name=new_crop)
                obj, created = FarmCrop.objects.get_or_create(
                    data=data,
                    farm=farm)
                if not created:
                    messages.info('crop {} was already allowed'.format(
                        new_crop))
            return HttpResponseRedirect(reverse('farm:farm', args=(farm.id, )))
    else:
        # GET or invalid form
        theform = form()

    if len(possible_crops) == 0:
        if farm.crops.count() < CropData.objects.count():
            messages.info(request,
                          "All known crops have been added to this farm.")
        return HttpResponseRedirect(
            reverse('farm:farm', args=(farm.id, )))

    theform.fields['crops'].choices = possible_crops

    context = dict(farm=farm, form=theform)
    return render(request, template_name, context)


@login_required
def editFarmCrop(request, pk):
    '''edit the overrides in farmcrop'''
    template_name = 'farm/edit_farmcrop.html'
    form = FarmCropForm

    crop = get_object_or_404(FarmCrop, pk=pk)

    if request.method == "POST":
        theform = form(request.POST, instance=crop)
        if theform.is_valid():
            theform.save()
            return HttpResponseRedirect(
                reverse('farm:farm', args=(crop.farm.id, )))
    else:
        # GET
        theform = form(instance=crop)

    context = dict(crop=crop, form=theform)
    return render(request, template_name, context)
