from django import forms

from .models import Farm
from optimizer.models import FarmCrop


class FarmExpenseForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['max_expense', ]


class FarmNoteForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'note', ]


class FarmAcreageForm(forms.ModelForm):
    class Meta:
        model = FarmCrop
        fields = ['lo_acres', 'hi_acres', ]

    def clean(self):
        cleaned_data = super().clean()
        low = cleaned_data.get('lo_acres')
        high = cleaned_data.get('hi_acres')
        if low and high and high > 0 and low > high:
            raise forms.ValidationError(
                'low is not lower than high')


class FarmCostForm(forms.ModelForm):
    class Meta:
        model = FarmCrop
        fields = ['cost_override', ]
