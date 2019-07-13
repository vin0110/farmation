from django.contrib import admin, auth
from django.urls import path

from django.views.generic import TemplateView

from .views import (home,
                    scenarioDetails,
                    scenarioEdit,
                    scenarioAdd,
                    cropDetails,
                    #cropEdit,
                    cropAdd,
                    )

urlpatterns = [
    path('scenario/details/<int:pk>/', scenarioDetails,
         name='scenario_details'),
    path('scenario/edit/<int:pk>/', scenarioEdit, name='scenario_edit'),
    path('scenario/add/', scenarioAdd, name='scenario_add'),

    path('crop/details/<int:pk>/', cropDetails, name='crop_details'),
    #path('crop/edit/<int:pk>/', cropEdit, name='crop_edit'),
    path('crop/add/<int:pk>/', cropAdd, name='crop_add'),

    path('', home, name='home'),
]
