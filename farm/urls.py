from django.urls import path

# from django.views.generic import TemplateView

from .views import (farm,
                    removeCropFromFarm,
                    addCropToFarm, )

urlpatterns = [
    path('<int:pk>/', farm, name='farm'),
    path('crop/rm/<int:pk>/<str:crop>/', removeCropFromFarm,
         name='remove_crop'),
    path('crop/add/<int:pk>/', addCropToFarm, name='add_crop'),
]
