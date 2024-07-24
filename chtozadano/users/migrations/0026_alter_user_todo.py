# Generated by Django 5.0.6 on 2024-07-26 01:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("homework", "0025_schedule_group"),
        ("users", "0025_alter_becomeadmin_grade_alter_user_grade_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="todo",
            field=models.ManyToManyField(
                blank=True, related_name="user_todo", to="homework.todo"
            ),
        ),
    ]
