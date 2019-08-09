from django.urls import path

from .views import (scenarioList,
                    scenarioDetails,
                    scenarioAdd,
                    cropDetails,
                    # cropEdit,
                    removeCropFromScenario,
                    addCropToScenario,
                    analyze,
                    )

urlpatterns = [
    path('scenario/details/<int:pk>/', scenarioDetails,
         name='scenario_details'),
    path('scenario/add/<int:pk>/', scenarioAdd, name='scenario_add'),

    path('scenario/crop/rm/<int:pk>/', removeCropFromScenario,
         name='rmCropScenario'),

    path('scenario/crop/add/<int:pk>/', addCropToScenario,
         name='addCropScenario'),

    path('crop/details/<int:pk>/', cropDetails, name='crop_details'),
    # path('crop/edit/<int:pk>/', cropEdit, name='crop_edit'),

    path('analyze/<int:pk>/', analyze, name='analyze'),

    path('<int:pk>/', scenarioList, name='list'),
]
