from django import forms
from calendar import month_name

MONTH_CHOICES = [(i, month_name[i]) for i in range(1, 13)]

from .models import (
    CROP_CHOICES,
    Location,
)


class QuantityForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    crop = forms.ChoiceField(choices=CROP_CHOICES)
    hedge_month = forms.ChoiceField(choices=MONTH_CHOICES)
    hedge_day = forms.IntegerField()
    reconciliation_month = forms.ChoiceField(choices=MONTH_CHOICES)
    reconciliation_day = forms.IntegerField()
    contract_month = forms.ChoiceField(choices=MONTH_CHOICES)
