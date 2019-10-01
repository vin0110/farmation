from django import forms

from .models import Farm


class FarmMaxEditForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['max_expense', ]
