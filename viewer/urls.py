from django.urls import path
from django.views.generic import TemplateView  # , RedirectView
# from braces.views import LoginRequiredMixin
# from django.contrib.auth.decorators import login_required

from .views import (
    field_crop_totals,
    vegetable_totals,
    fruit_tree_totals,
    horticulture_totals,
    crop_totals,
    livestock_totals,
    poultry_totals,
    dairy_totals,
    aquaculture_totals,
    specialty_totals,
    county_production_totals,
    area_planted_harvested_by_crop,
    area_planted_harvested_by_year,
    area_planted_harvested_by_crop_county,
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
    path('livestock_totals/', livestock_totals, name='livestock_totals'),
    path('poultry_totals/', poultry_totals, name='poultry_totals'),
    path('dairy_totals/', dairy_totals, name='dairy_totals'),
    path('aquaculture_totals/', aquaculture_totals, name='aquaculture_totals'),
    path('specialty_totals/', specialty_totals, name='specialty_totals'),
    path('county_production_totals/', county_production_totals,
         name='county_production_totals'),
    path('area_planted_harvested_by_crop/', area_planted_harvested_by_crop,
         name='area_planted_harvested_by_crop'),
    path('area_planted_harvested_by_year/', area_planted_harvested_by_year,
         name='area_planted_harvested_by_year'),

    path('select_state', TemplateView.as_view(template_name='tbd.html'),
         name='select_state'),
    path('area_planted_harvested_by_crop/<str:state>/',
         area_planted_harvested_by_crop_county,
         name='area_planted_harvested_by_crop_county'),
]
