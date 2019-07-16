from django.contrib import admin

from .models import Scenario, Crop

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    pass

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'scenarioName', 'farmName', 'userName', )


