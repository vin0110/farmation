from django import forms
from django.conf import settings

from .models import Scenario


class ScenarioEditForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['name', ]


class CropAcresSetForm(forms.Form):
    low = forms.IntegerField(min_value=0)
    high = forms.IntegerField(min_value=0,
                              help_text="0 means unlimited")


class AddCropForm(forms.Form):
    '''select a crop. the list is dynamic; set none here; view will expand'''
    crop = forms.ChoiceField(choices=[])
