from django.contrib.auth import get_user_model
from django.db import models

import homework.models

DjangoUser = get_user_model()


class User(models.Model):
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    grade = models.IntegerField(null=True, blank=True)
    letter = models.CharField(null=True, blank=True)
    telegram_id = models.IntegerField(null=True, blank=True)
    notebook = models.TextField(null=True, blank=True)
    homework = models.ManyToManyField(
        homework.models.Homework,
        related_name="author",
        blank=True,
    )

    def __str__(self):
        return self.user.username
