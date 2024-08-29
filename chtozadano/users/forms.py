import django.forms
from django.forms import Form

from homework.forms import GRADE_CHOICES, GROUP_CHOICES, LETTER_CHOICES


class SignUpForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
        label="Код идентификации",
    )
    grade = django.forms.ChoiceField(choices=GRADE_CHOICES, label="Класс")
    letter = django.forms.ChoiceField(choices=LETTER_CHOICES, label="Литера")
    group = django.forms.ChoiceField(choices=GROUP_CHOICES, label="Группа")


class SignInForm(Form):
    confirmation_code = django.forms.IntegerField(
        min_value=10000,
        max_value=999999,
        label="Код идентификации",
    )


class SignUpPasswordForm(Form):
    username = django.forms.CharField(max_length=255, label="Логин")
    password = django.forms.CharField(
        widget=django.forms.PasswordInput,
        label="Пароль",
    )
    repeat_password = django.forms.CharField(
        widget=django.forms.PasswordInput,
        label="Повторите пароль",
    )
    grade = django.forms.ChoiceField(choices=GRADE_CHOICES, label="Класс")
    letter = django.forms.ChoiceField(choices=LETTER_CHOICES, label="Литера")
    group = django.forms.ChoiceField(choices=GROUP_CHOICES, label="Группа")


class SignInPasswordForm(Form):
    username = django.forms.CharField(max_length=255, label="Логин")
    password = django.forms.CharField(
        widget=django.forms.PasswordInput,
        label="Пароль",
    )


class ChangeContactsForm(Form):
    first_name = django.forms.CharField(label="Имя")
    last_name = django.forms.CharField(required=False, label="Фамилия")
