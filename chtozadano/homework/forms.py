from django import forms

from users.models import GRADE_CHOICES, LETTER_CHOICES


GROUP_CHOICES = (
    (1, 1),
    (2, 2),
)


class ChooseGradLetForm(forms.Form):
    grade = forms.ChoiceField(choices=GRADE_CHOICES)
    letter = forms.ChoiceField(choices=LETTER_CHOICES)
    group = forms.ChoiceField(choices=GROUP_CHOICES)
