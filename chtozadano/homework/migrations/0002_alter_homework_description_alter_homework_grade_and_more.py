# Generated by Django 5.0.6 on 2024-06-29 22:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("homework", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homework",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="homework",
            name="grade",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(11),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="homework",
            name="letter",
            field=models.CharField(max_length=1),
        ),
    ]
