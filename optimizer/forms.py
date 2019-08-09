from django import forms

from .models import Scenario, FarmCrop, Crop


class ScenarioEditForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['name', ]


class CropAcresSetForm(forms.Form):
    low = forms.IntegerField(min_value=0)
    high = forms.IntegerField(min_value=0,
                              help_text="0 means unlimited")


class AddMultipleCropForm(forms.Form):
    '''select a crop. the list is dynamic; set none here; view will expand'''
    crops = forms.MultipleChoiceField(choices=[])


class FarmCropForm(forms.ModelForm):
    class Meta:
        model = FarmCrop
        fields = ['lo_acres', 'hi_acres', 'yield_override', 'cost_override', ]


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['lo_acres', 'hi_acres', 'yield_override', 'cost_override', ]
