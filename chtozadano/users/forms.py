import django.forms
from django.forms import Form


class SignUpForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
    )
    grade = django.forms.IntegerField(min_value=1, max_value=11)
    letter = django.forms.CharField(max_length=1, min_length=1)


class SignInForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
    )
