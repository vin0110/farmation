from django.contrib import admin
from .models import Farm, Field


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    pass


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'farmUser')
