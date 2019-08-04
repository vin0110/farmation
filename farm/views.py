from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from farm.models import Farm


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
    template_name = 'optimizer/add_crop_to_farm.html'
    form = AddCropForm

    farm = get_object_or_404(Farm, pk=pk)
    if scenario.farm.user != request.user:
        raise Http404

    if request.method == "POST":
        print('post', request.POST)
        theform = form(request.POST)
        if theform.is_valid():
            name = theform.cleaned_data['crop']
            crop = Crop.objects.create(name=name, farm=farm)
            scenario.crops.add(crop)
            print('n', name, crop)
            return HttpResponseRedirect(
                reverse('optimizer:farm_details', args=(farm.id, )))
    else:
        # GET or invalid form
        theform = form()

    possible_crops = []
    farm_crops = scenario.farm.getCrops()
    for crop in farm_crops:
        try:
            scenario.crops.get(name=crop)
            # crop is in the list; it is not possible
        except Crop.DoesNotExist:
            possible_crops.append((crop, crop))
    if len(possible_crops) == 0:
        if len(farm_crops) < CropData.objects.count():
            msg = "All crops allowed in this farm have been added. "\
                  "Must reconfigure farm to add more crops."
        else:
            msg = 'All crops have been added to this scenario.'
        messages.info(request, msg)
        return HttpResponseRedirect(
            reverse('optimizer:scenario_details', args=(scenario.id, )))

    theform.fields['crop'].choices = possible_crops

    context = dict(scenario=scenario, form=theform)
    return render(request, template_name, context)
