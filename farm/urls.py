from django.urls import path

# from django.views.generic import TemplateView

from .views import (farm,
                    add_farm,
                    removeCropFromFarm,
                    addCropToFarm,
                    editExpense,
                    editNote,
                    editAcres,
                    editCost,
                    )

urlpatterns = [
    path('<int:pk>/', farm, name='farm'),
    path('add/', add_farm, name='add_farm'),
    path('crop/rm/<int:pk>/', removeCropFromFarm,
         name='remove_crop'),
    path('crop/add/<int:pk>/', addCropToFarm, name='add_crop'),

    path('edit/expense/<int:pk>/', editExpense, name='edit_expense',),
    path('edit/note/<int:pk>/', editNote, name='edit_note',),
    path('edit/acres/<int:pk>/', editAcres, name='edit_acres',),

    path('edit/cost/<int:pk>/', editCost, name='edit_cost',),
    path('edit/cost/reset/<int:pk>/', editCost, dict(reset=True), name='reset_cost',),
]
