# Generated by Django 5.0.6 on 2024-07-31 23:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("homework", "0027_homework_author"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="schedule",
            options={"verbose_name": "Расписание", "verbose_name_plural": "Расписания"},
        ),
    ]
