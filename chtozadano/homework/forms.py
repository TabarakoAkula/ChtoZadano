from django import forms


class ChooseGradLetForm(forms.Form):
    grade = forms.IntegerField(min_value=1, max_value=11)
    letter = forms.CharField(max_length=1)
