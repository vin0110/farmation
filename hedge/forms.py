from django import forms
from calendar import month_name

MONTH_CHOICES = [(i, month_name[i]) for i in range(1, 13)]

from .models import (
    CROP_CHOICES,
    Location,
)


class QuantityForm(forms.Form):
    hedge_date = forms.CharField(min_length=5, max_length=5, help_text="MM-DD")
    reconcilliation_date = forms.CharField(
        min_length=5, max_length=5, help_text="MM-DD")
    contract_month = forms.ChoiceField(choices=MONTH_CHOICES)


class ContractForm(forms.Form):
    hedge_date = forms.CharField(min_length=5, max_length=5, help_text="MM-DD")
    reconcilliation_date = forms.CharField(
        min_length=5, max_length=5, help_text="MM-DD")
    quantity = forms.IntegerField()
    # contract_month = forms.MultipleChoiceField(choices=MONTH_CHOICES)


class ReconForm(forms.Form):
    hedge_date = forms.CharField(min_length=5, max_length=5, help_text="MM-DD")
    reconcilliation_day = forms.IntegerField(help_text="DD")
    quantity = forms.IntegerField()
    contract_month = forms.ChoiceField(choices=MONTH_CHOICES)
    reconciliation_months = forms.MultipleChoiceField(choices=MONTH_CHOICES)


class CropForm(forms.Form):
    crop = forms.ChoiceField(choices=CROP_CHOICES)


class LocationForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all())
