from django.contrib import admin

from .models import CropData, Scenario, Crop, FarmCrop, PriceOrder


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    pass


def scenario_user(crop):
    return crop.scenario.farm.user


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('data', 'scenario', scenario_user)


def farm_user(farmcrop):
    return farmcrop.farm.user


@admin.register(FarmCrop)
class FarmCropAdmin(admin.ModelAdmin):
    list_display = ('data', 'farm', farm_user, )


@admin.register(CropData)
class CropDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', )


@admin.register(PriceOrder)
class PriceOrderAdmin(admin.ModelAdmin):
    list_display = ('crop', 'units', 'price', 'safety', )
