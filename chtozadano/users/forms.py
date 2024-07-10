import django.forms
from django.forms import Form


class SignUpForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
    )
    grade = django.forms.IntegerField(min_value=4, max_value=11)
    letter = django.forms.CharField(max_length=1, min_length=1)
    group = django.forms.IntegerField(max_value=2, min_value=1)


class SignInForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
    )


class SignUpPasswordForm(Form):
    username = django.forms.CharField(max_length=255)
    password = django.forms.CharField(widget=django.forms.PasswordInput)
    repeat_password = django.forms.CharField(widget=django.forms.PasswordInput)
    grade = django.forms.IntegerField(min_value=4, max_value=11)
    letter = django.forms.CharField(max_length=1, min_length=1)
    group = django.forms.IntegerField(max_value=2, min_value=1)


class SignInPasswordForm(Form):
    username = django.forms.CharField(max_length=255)
    password = django.forms.CharField(widget=django.forms.PasswordInput)


class ChangeContactsForm(Form):
    first_name = django.forms.CharField()
    last_name = django.forms.CharField(required=False)
