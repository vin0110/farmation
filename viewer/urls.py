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
    # county_field_crop_totals,
    # county_vegetable_totals,
    # county_fruit_tree_totals,
    # county_horticulture_totals,
    # county_crop_totals,
    livestock_totals,
    poultry_totals,
    dairy_totals,
    aquaculture_totals,
    specialty_totals,
    # county_production_totals,
    area_planted_harvested_by_crop,
    area_planted_harvested_by_year,
)


urlpatterns = [
    path('', TemplateView.as_view(template_name="viewer/index.html"),
         name='home'),
    path('field_crop_totals/', field_crop_totals, name='field_crop_totals',),
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

    path('area_planted_harvested_by_crop/', area_planted_harvested_by_crop,
         name='area_planted_harvested_by_crop'),
    path('area_planted_harvested_by_year/', area_planted_harvested_by_year,
         name='area_planted_harvested_by_year'),

    path('production/',
         TemplateView.as_view(template_name='viewer/production_index.html'),
         name='production'),

    path('county/production/<str:state>/',
         TemplateView.as_view(template_name='viewer/production_index.html'),
         name='production'),

    path('select_state',
         TemplateView.as_view(template_name='viewer/select_state.html'),
         name='select_state'),

    path('county/field_crop_totals/<str:state>/',
         field_crop_totals, name='field_crop_totals'),
    path('county/vegetable_totals/<str:state>/',
         vegetable_totals, name='vegetable_totals'),
    path('county/fruit_tree_totals/<str:state>/',
         fruit_tree_totals, name='fruit_tree_totals'),
    path('county/horticulture_totals/<str:state>/',
         horticulture_totals, name='horticulture_totals'),
    path('county_livestock_totals/<str:state>/',
         livestock_totals, name='livestock_totals'),
    path('county_poultry_totals/<str:state>/',
         poultry_totals, name='poultry_totals'),
    path('county_dairy_totals/<str:state>/',
         dairy_totals, name='dairy_totals'),
    path('county_aquaculture_totals/<str:state>/',
         aquaculture_totals, name='aquaculture_totals'),
    path('county_specialty_totals/<str:state>/',
         specialty_totals, name='specialty_totals'),
]
