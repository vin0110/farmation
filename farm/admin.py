from django.contrib import admin
from .models import Farm, Field


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', )


def farm_user(field):
    return field.farm.user

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', farm_user, )
