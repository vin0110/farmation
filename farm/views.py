from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from farm.models import Farm

def farm(request):
    '''display the specifics of the farm'''
    
    template_name = 'farm/farm.html'

    # @@@ only one farm for now
    farm = Farm.objects.first()
    context = dict(farm=farm,
                   fields=farm.fields(), )
    return HttpResponse(render(request, template_name, context))
