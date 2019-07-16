from django.contrib import admin, auth
from django.urls import path

from django.views.generic import TemplateView

from .views import farm

urlpatterns = [
    path('<int:pk>/', farm, name='farm'),
]
