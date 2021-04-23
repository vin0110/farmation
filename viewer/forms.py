from django import forms


class StateYearForm(forms.Form):
    state = forms.CharField(label="state")
    year = forms.CharField(label="year", required=False)
