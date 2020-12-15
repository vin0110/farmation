from django.urls import path

from django.views.generic import TemplateView

from .views import (
    quantity,
)

urlpatterns = [
    path('',
         TemplateView.as_view(template_name='hedge/index.html'),
         name='index'),
    path('quantity/', quantity, name='quantity'),
    # path('quantity/', quantity, dict(blank=True), name='quantity_blank'),
]
