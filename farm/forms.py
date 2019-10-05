from django import forms

from .models import Farm


class FarmExpenseForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['max_expense', ]


class FarmNoteForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['note', ]
