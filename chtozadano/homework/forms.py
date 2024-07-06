from django import forms

from users.models import GRADE_CHOICES, LETTER_CHOICES


class ChooseGradLetForm(forms.Form):
    grade = forms.ChoiceField(choices=GRADE_CHOICES)
    letter = forms.ChoiceField(choices=LETTER_CHOICES)
    group = forms.IntegerField(max_value=2, min_value=1)
