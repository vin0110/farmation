from django import forms


class StateYearForm(forms.Form):
    state = forms.CharField(label="state")
    year = forms.CharField(label="year", required=False)


class StateCropForm(forms.Form):
    state = forms.CharField(label="state")
    crop = forms.CharField(label="crop", required=False)
