from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import (Farm, Field, )
from optimizer.models import CropData, FarmCrop
from optimizer.forms import AddMultipleCropForm
from .forms import (FarmExpenseForm,
                    FarmNoteForm,
                    FarmAcreageForm,
                    FarmCostForm,
                    )


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
    expense_form = FarmExpenseForm(instance=farm)
    note_form = FarmNoteForm(instance=farm)

    context = dict(farm=farm, expense_form=expense_form, note_form=note_form)
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
    theform = AddMultipleCropForm

    farm = get_object_or_404(Farm, pk=pk, user=request.user)

    possible_crops = []
    for data in CropData.objects.all():
        try:
            farm.crops.get(data=data)
        except FarmCrop.DoesNotExist:
            possible_crops.append((data.name, data.name))

    if request.method == "POST":
        form = theform(request.POST)
        form.fields['crops'].choices = possible_crops

        if form.is_valid():
            selected_crops = form.cleaned_data['crops']
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
        form = theform()
        form.fields['crops'].choices = possible_crops

    if len(possible_crops) == 0:
        messages.info(request,
                      "All crops have been added to this farm.")
        return HttpResponseRedirect(
            reverse('farm:farm', args=(farm.id, )))

    context = dict(farm=farm, form=form)
    return render(request, template_name, context)


@login_required
def editAcres(request, pk):
    '''edit the overrides in farmcrop'''
    template_name = 'farm/edit_acres.html'
    theform = FarmAcreageForm

    crop = get_object_or_404(FarmCrop, pk=pk, farm__user=request.user)

    if request.method == "POST":
        form = theform(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('farm:farm', args=(crop.farm.id, )))
    else:
        # GET
        form = theform(instance=crop)

    context = dict(crop=crop, form=form)
    return render(request, template_name, context)


@login_required
def editCost(request, pk, reset=False):
    '''edit the overrides in farmcrop'''
    template_name = 'farm/edit_cost.html'
    theform = FarmCostForm

    crop = get_object_or_404(FarmCrop, pk=pk, farm__user=request.user)

    if reset:
        crop.cost_override = 0.0
        crop.save()
        return HttpResponseRedirect(
            reverse('farm:farm', args=(crop.farm.id, )))

    if request.method == "POST":
        form = theform(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('farm:farm', args=(crop.farm.id, )))
    else:
        # GET
        form = theform(instance=crop)

    reset_url = reverse('farm:reset_cost', args=(crop.id, ))
    context = dict(crop=crop, form=form, reset_url=reset_url)
    return render(request, template_name, context)


@login_required
def editExpense(request, pk):
    '''edit the overrides in farmcrop'''
    theform = FarmExpenseForm

    farm = get_object_or_404(Farm, pk=pk, user=request.user)

    if request.method == "POST":
        form = theform(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('farm:farm', args=(farm.id, )))
    else:
        raise Http404


@login_required
def editNote(request, pk):
    '''edit the overrides in farmcrop'''
    theform = FarmNoteForm

    farm = get_object_or_404(Farm, pk=pk, user=request.user)

    if request.method == "POST":
        form = theform(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('farm:farm', args=(farm.id, )))
    else:
        raise Http404
