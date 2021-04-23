from django.urls import path
from django.views.generic import TemplateView  # , RedirectView
# from braces.views import LoginRequiredMixin
# from django.contrib.auth.decorators import login_required

from .views import (
    field_crop_totals,
    vegetable_totals,
    fruit_tree_totals,
    horticulture_totals,
    crop_totals
)


urlpatterns = [
    path('', TemplateView.as_view(template_name="viewer/index.html"),
         name='home'),
    path('field_crop_totals/', field_crop_totals, name='field_crop_totals'),
    path('vegetable_totals/', vegetable_totals, name='vegetable_totals'),
    path('fruit_tree_totals/', fruit_tree_totals, name='fruit_tree_totals'),
    path('horticulture_totals/', horticulture_totals,
         name='horticulture_totals'),
    path('crop_totals/', crop_totals, name='crop_totals'),
]
