from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
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
