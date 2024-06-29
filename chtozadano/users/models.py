from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
import django.db.models

from homework.models import Homework

DjangoUser = get_user_model()


class User(django.db.models.Model):
    user = django.db.models.OneToOneField(
        DjangoUser,
        on_delete=django.db.models.CASCADE,
        primary_key=True,
    )
    grade = django.db.models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(11)],
    )
    letter = django.db.models.CharField(max_length=1)
    telegram_id = django.db.models.IntegerField()
    notebook = django.db.models.TextField(null=True, blank=True)
    homework = django.db.models.ManyToManyField(
        Homework,
        related_name="author",
        blank=True,
    )

    def __str__(self):
        return self.user.username


class SignIn(django.db.models.Model):
    user = django.db.models.OneToOneField(
        User,
        on_delete=django.db.models.DO_NOTHING,
        null=True,
        blank=True,
    )
    telegram_id = django.db.models.IntegerField(null=True, blank=True)
    confirmation_code = django.db.models.CharField(null=True, blank=True)
    created_at = django.db.models.DateTimeField(auto_now_add=True)
    name = django.db.models.CharField(null=True, blank=True)

    def __str__(self):
        return self.id


class Todo(django.db.models.Model):
    user = django.db.models.OneToOneField(
        User,
        on_delete=django.db.models.DO_NOTHING,
    )
    homework = django.db.models.OneToOneField(
        Homework,
        on_delete=django.db.models.DO_NOTHING,
    )
    is_done = django.db.models.BooleanField(default=False)

    def __str__(self):
        return f"{self.is_done} | {self.user} | {self.homework}"
