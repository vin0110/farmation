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


class FarmCostForm(forms.ModelForm):
    class Meta:
        model = FarmCrop
        fields = ['cost_override', ]
