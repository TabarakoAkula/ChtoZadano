from django import forms

from users.models import GRADE_CHOICES, LETTER_CHOICES


GROUP_CHOICES = (
    ("Вахрушев_Д.В.", "Вахрушев Д.В."),
    ("Красноухова_Л.А.", "Красноухова Л.А."),
    ("Шерепа_Е.А.", "Шерепа Е.А."),
    ("Зелинская_Ю.Л.", "Зелинская Ю.Л."),
    ("Краснобаева_И.В.", "Краснобаева И.В."),
    ("Каменкова_М.М.", "Каменкова М.М."),
    ("Гермогенова_Н.Н.", "Гермогенова Н.Н."),
    ("Власюк_И.А.", "Власюк И.А."),
    ("Чадаева_С.В.", "Чадаева С.В."),
    ("Доброниченко_Е.В.", "Доброниченко Е.В."),
    ("Курганова_Е.П.", "Курганова Е.П."),
)


class ChooseGradLetForm(forms.Form):
    grade = forms.ChoiceField(choices=GRADE_CHOICES, label="Класс")
    letter = forms.ChoiceField(choices=LETTER_CHOICES, label="Литера")
    group = forms.ChoiceField(choices=GROUP_CHOICES, label="Группа")
