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
    'cost_override':
    'additive: 0.0 is no change; 150.0 increases cost by $150.00',
}


class FarmCropForm(forms.ModelForm):
    class Meta:
        model = FarmCrop
        fields = ['lo_acres', 'hi_acres', 'cost_override', ]
        help_texts = HELP_TEXTS


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['lo_acres', 'hi_acres', 'cost_override', ]
        help_texts = HELP_TEXTS


class EditYieldForm(forms.Form):
    '''edit the crop yield triangle'''
    low = forms.FloatField(min_value=0.0)
    peak = forms.FloatField(min_value=0.0)
    high = forms.FloatField(min_value=0.0)

    def clean(self):
        cleaned_data = super().clean()
        low = cleaned_data.get('low')
        peak = cleaned_data.get('peak')
        high = cleaned_data.get('high')
        if not low < peak < high:
            raise forms.ValidationError(
                'failed assertation: low < peak < high')


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
