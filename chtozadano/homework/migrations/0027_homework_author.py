# Generated by Django 5.0.6 on 2024-07-31 02:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("homework", "0026_homework_homework_ho_grade_d37973_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="homework",
            name="author",
            field=models.CharField(default="Anonym", verbose_name="Автор"),
        ),
    ]
