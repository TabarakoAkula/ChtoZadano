# Generated by Django 5.0.6 on 2024-06-29 16:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_signin"),
    ]

    operations = [
        migrations.RenameField(
            model_name="signin",
            old_name="user_id",
            new_name="user",
        ),
    ]
