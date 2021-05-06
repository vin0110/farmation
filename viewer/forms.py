from django import forms


class StateYearForm(forms.Form):
    state = forms.CharField(label="state")
    year = forms.CharField(label="year", required=False)


class StateCropForm(forms.Form):
    state = forms.CharField(label="state")
    crop = forms.CharField(label="crop", required=False)


class CountyYearForm(forms.Form):
    county = forms.ChoiceField(label="county", choices=[])
    year = forms.CharField(label="year", required=False)

    def __init__(self, *args, **kwargs):
        county_choices = kwargs.pop('county_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['county'].choices = county_choices
