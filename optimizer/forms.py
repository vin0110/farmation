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


class EditTriangleForm(forms.Form):
    '''edit triangle distro'''
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
        ('Very high', 'Very high'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
        ('Very low', 'Very low'), ], initial="Medium", )

    class Meta:
        model = PriceOrder
        fields = ['units', 'price', 'safety', ]
        help_texts = {
            'units': 'number of units',
            'price': 'price per unit',
            'safety': 'extra acreage planted to ensure sufficient crop',
        }


class AcreageForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['lo_acres', 'hi_acres', ]

    def clean(self):
        cleaned_data = super().clean()
        low = cleaned_data.get('lo_acres')
        high = cleaned_data.get('hi_acres')
        if low and high and high > 0 and low > high:
            raise forms.ValidationError(
                'low is not lower than high')


class CostForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['cost_override', ]
