# Generated by Django 5.0.6 on 2024-07-01 08:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("homework", "0002_alter_homework_description_alter_homework_grade_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="File",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file_path", models.FileField(upload_to="files/homework/%Y/%d-%m/")),
            ],
        ),
        migrations.AlterField(
            model_name="image",
            name="image_path",
            field=models.ImageField(upload_to="img/homework/%Y/%d-%m/"),
        ),
        migrations.AddField(
            model_name="homework",
            name="file",
            field=models.ManyToManyField(blank=True, to="homework.file"),
        ),
    ]
