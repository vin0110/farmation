from django.urls import path

from .views import (scenarioList,
                    scenarioDetails,
                    scenarioAdd,
                    scenarioDelete,
                    scenarioReload,
                    cropData,
                    editCost,
                    editCrop,
                    editAcres,
                    editTriangle,
                    addPrice,
                    editPrice,
                    removePrice,
                    removeCropFromScenario,
                    addCropToScenario,
                    updateScenario,
                    partitionDetails,
                    analyze,
                    )

urlpatterns = [
    path('scenario/details/<int:pk>/', scenarioDetails,
         name='scenario_details'),
    path('scenario/add/<int:pk>/', scenarioAdd, name='scenario_add'),
    path('scenario/delete/<int:pk>/', scenarioDelete,
         name='scenario_delete'),

    path('scenario/crop/rm/<int:pk>/', removeCropFromScenario,
         name='rmCropScenario'),

    path('scenario/crop/add/<int:pk>/', addCropToScenario,
         name='addCropScenario'),

    path('scenario/update/<int:pk>/', updateScenario, name='updateScenario'),
    path('scenario/reload/<int:pk>/', scenarioReload, name='scenario_reload'),
    path('scenario/<int:pk>/partition/<int:part>/', partitionDetails,
         name='partition_details'),

    path('crop/data/<int:pk>/', cropData, name='crop_data'),
    path('crop/edit/<int:pk>/', editCrop, name='edit_crop'),

    path('crop/yield/<int:pk>/', editTriangle,
         dict(which='yield', ), name='edit_crop_yield'),
    path('crop/yield/reset/<int:pk>/', editTriangle,
         dict(which='yield', reset=True, ), name='reset_crop_yield'),
    path('crop/price/<int:pk>/', editTriangle,
         dict(which='price', ), name='edit_crop_price'),
    path('crop/price/reset/<int:pk>/', editTriangle,
         dict(which='price', reset=True, ), name='reset_crop_price'),

    path('crop/price/add/<int:pk>/', addPrice, name='add_price'),
    path('crop/price/edit/<int:pk>/', editPrice, name='edit_price'),
    path('crop/price/rm/<int:pk>/', removePrice, name='remove_price'),

    path('crop/edit/cost/<int:pk>/', editCost, name='edit_cost'),
    path('crop/edit/acres/<int:pk>/', editAcres, name='edit_acres'),

    path('analyze/<int:pk>/', analyze, name='analyze'),

    path('<int:pk>/', scenarioList, name='list'),
]
