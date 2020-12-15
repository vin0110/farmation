from django.urls import path

from django.views.generic import TemplateView

from .views import (
    quantity,
)

urlpatterns = [
    path('',
         TemplateView.as_view(template_name='hedge/index.html'),
         name='index'),
    path('quantity/<int:loc>/<int:hday>/<int:hmon>/<int:rday>/'
         '<int:rmon>/<int:month>/',
         quantity,
         name='quantity'),
]
