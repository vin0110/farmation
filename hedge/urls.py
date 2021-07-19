from django.urls import path

# from django.views.generic import TemplateView

from .views import (
    quantity,
    contract,
    recon,
    wizard,
    wizard_crop,
    wizard_select,
)

urlpatterns = [
    path('', wizard, name='index'),
    path('quantity/<str:crop>/<int:lid>/', quantity, name='quantity'),
    path('contract/<str:crop>/<int:lid>/', contract, name='contract'),
    path('recon_dates/<str:crop>/<int:lid>/', recon, name='recon'),
    path('<str:crop>/', wizard_crop, name='wizard_crop'),
    path('<str:crop>/<int:lid>/', wizard_select, name='select'),

]
