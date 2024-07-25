import django.forms
from django.forms import Form

from homework.forms import GRADE_CHOICES, GROUP_CHOICES, LETTER_CHOICES

COLOR_CHOICES = ["#8b0000", "#ffff00", "#006400"]


class SignUpForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
    )
    grade = django.forms.ChoiceField(choices=GRADE_CHOICES)
    letter = django.forms.ChoiceField(choices=LETTER_CHOICES)
    group = django.forms.ChoiceField(choices=GROUP_CHOICES)


class SignInForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
    )


class SignUpPasswordForm(Form):
    username = django.forms.CharField(max_length=255)
    password = django.forms.CharField(widget=django.forms.PasswordInput)
    repeat_password = django.forms.CharField(widget=django.forms.PasswordInput)
    grade = django.forms.ChoiceField(choices=GRADE_CHOICES)
    letter = django.forms.ChoiceField(choices=LETTER_CHOICES)
    group = django.forms.ChoiceField(choices=GROUP_CHOICES)


class SignInPasswordForm(Form):
    username = django.forms.CharField(max_length=255)
    password = django.forms.CharField(widget=django.forms.PasswordInput)


class ChangeContactsForm(Form):
    first_name = django.forms.CharField()
    last_name = django.forms.CharField(required=False)


class EditNotebookForm(Form):
    text = django.forms.CharField(widget=django.forms.Textarea)
