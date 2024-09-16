# Generated by Django 5.0.6 on 2024-09-16 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='send_analytics',
            field=models.BooleanField(default=False, verbose_name='Отправка аналитики'),
        ),
        migrations.AddField(
            model_name='user',
            name='send_cleaner',
            field=models.BooleanField(default=False, verbose_name='Отправка очистки'),
        ),
    ]
