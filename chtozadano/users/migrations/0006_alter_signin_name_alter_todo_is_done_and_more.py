# Generated by Django 5.0.6 on 2024-06-29 22:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_signin_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="signin",
            name="name",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="todo",
            name="is_done",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="grade",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(11),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="letter",
            field=models.CharField(max_length=1),
        ),
        migrations.AlterField(
            model_name="user",
            name="telegram_id",
            field=models.IntegerField(),
        ),
    ]
