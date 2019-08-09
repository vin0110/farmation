from django.urls import path

# from django.views.generic import TemplateView

from .views import (farm,
                    removeCropFromFarm,
                    addCropToFarm,
                    editFarmCrop, )

urlpatterns = [
    path('<int:pk>/', farm, name='farm'),
    path('crop/rm/<int:pk>/', removeCropFromFarm,
         name='remove_crop'),
    path('crop/add/<int:pk>/', addCropToFarm, name='add_crop'),

    path('crop/edit/<int:pk>/', editFarmCrop, name='edit_crop'),
]
