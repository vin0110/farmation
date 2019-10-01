from django import forms

from .models import Scenario, FarmCrop, Crop, PriceOrder


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


HELP_TEXTS = {
    'lo_acres': 'zero (0) means no limit set',
    'hi_acres': 'zero (0) means no limit set',
    'yield_override':
    'multiplitive:; 1.0 is no change ; 1.1 increases yield by 10%',
    'cost_override':
    'additive: 0.0 is no change; 1.50 increases cost by $1.50',
}


class FarmCropForm(forms.ModelForm):
    class Meta:
        model = FarmCrop
        fields = ['lo_acres', 'hi_acres', 'yield_override', 'cost_override', ]
        help_texts = HELP_TEXTS


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['lo_acres', 'hi_acres', 'yield_override', 'cost_override', ]
        help_texts = HELP_TEXTS


class PriceOrderForm(forms.ModelForm):
    safety = forms.ChoiceField(choices=[
        (90, 'Very high'),
        (75, 'High'),
        (50, 'Medium'),
        (25, 'Low'),
        (10, 'Very low'), ])

    class Meta:
        model = PriceOrder
        fields = ['units', 'price', 'safety', ]
        help_texts = {
            'units': 'number of units',
            'price': 'price per unit',
            'safety': 'extra acreage planted to ensure sufficient crop',
        }
