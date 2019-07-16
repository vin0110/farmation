from django.urls import path

from .views import (scenarioList,
                    scenarioDetails,
                    scenarioEdit,
                    scenarioAdd,
                    cropDetails,
                    # cropEdit,
                    cropAdd,
                    analyze,
                    )

urlpatterns = [
    path('scenario/details/<int:pk>/', scenarioDetails,
         name='scenario_details'),
    path('scenario/edit/<int:pk>/', scenarioEdit, name='scenario_edit'),
    path('scenario/add/<int:pk>/', scenarioAdd, name='scenario_add'),

    path('crop/details/<int:pk>/', cropDetails, name='crop_details'),
    # path('crop/edit/<int:pk>/', cropEdit, name='crop_edit'),
    path('crop/add/<int:pk>/', cropAdd, name='crop_add'),

    path('analyze/<int:pk>/', analyze, name='analyze'),

    path('<int:pk>/', scenarioList, name='list'),
]
