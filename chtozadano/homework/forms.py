import django.forms
from django.forms import Form


class ChooseGradLetForm(Form):
    grade = django.forms.IntegerField(min_value=1, max_value=11)
    letter = django.forms.CharField(max_length=1)
