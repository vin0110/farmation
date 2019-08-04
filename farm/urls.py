from django.urls import path

# from django.views.generic import TemplateView

from .views import (farm,
                    removeCropFromFarm, )

urlpatterns = [
    path('<int:pk>/', farm, name='farm'),
    path('crop/rm/<int:pk>/<str:crop>/', removeCropFromFarm,
         name='remove_crop'),
]
