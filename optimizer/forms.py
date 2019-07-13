from django import forms

from .models import Scenario

class ScenarioEditForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['name', ]

CROPS = ['corn', 'soybeans', 'wheat', 'hay', ]

CROP_CHOICES = [(n, n, ) for n in CROPS]

class CropAddForm(forms.Form):
    name = forms.ChoiceField(choices=CROP_CHOICES)
