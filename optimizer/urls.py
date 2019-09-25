from django.urls import path

from .views import (scenarioList,
                    scenarioDetails,
                    scenarioAdd,
                    cropDetails,
                    editCrop,
                    addPrice,
                    editPrice,
                    removePrice,
                    removeCropFromScenario,
                    addCropToScenario,
                    updateScenario,
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

    path('scenario/update/<int:pk>/', updateScenario, name='updateScenario'),

    path('crop/details/<int:pk>/', cropDetails, name='crop_details'),
    path('crop/edit/<int:pk>/', editCrop, name='edit_crop'),

    path('crop/price/add/<int:pk>/', addPrice, name='add_price'),
    path('crop/price/edit/<int:pk>/', editPrice, name='edit_price'),
    path('crop/price/rm/<int:pk>/', removePrice, name='remove_price'),

    path('analyze/<int:pk>/', analyze, name='analyze'),

    path('<int:pk>/', scenarioList, name='list'),
]
