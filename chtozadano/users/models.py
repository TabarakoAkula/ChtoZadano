from django.contrib.auth import get_user_model
import django.db.models

from homework.models import Homework

DjangoUser = get_user_model()

GRADE_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11),
)

LETTER_CHOICES = (
    ("А", "А"),
    ("Б", "Б"),
    ("Г", "В"),
    ("Г", "В"),
)


class DateTimeWithoutTZField(django.db.models.DateTimeField):
    def db_type(self, connection):
        return "timestamp"


class User(django.db.models.Model):
    user = django.db.models.OneToOneField(
        DjangoUser,
        on_delete=django.db.models.CASCADE,
        primary_key=True,
        related_name="server_user",
    )
    grade = django.db.models.IntegerField(choices=GRADE_CHOICES)
    letter = django.db.models.CharField(choices=LETTER_CHOICES)
    telegram_id = django.db.models.CharField()
    group = django.db.models.IntegerField(choices=((1, 1), (2, 2)), default=1)
    notebook = django.db.models.TextField(null=True, blank=True)
    chat_mode = django.db.models.BooleanField(default=False)
    homework = django.db.models.ManyToManyField(
        Homework,
        related_name="author",
        blank=True,
    )

    def __str__(self):
        return self.user.username


class SignIn(django.db.models.Model):
    singning_user = django.db.models.OneToOneField(
        User,
        on_delete=django.db.models.DO_NOTHING,
        null=True,
        blank=True,
    )
    telegram_id = django.db.models.CharField(null=True, blank=True)
    confirmation_code = django.db.models.CharField(null=True, blank=True)
    created_at = DateTimeWithoutTZField(auto_now_add=True)
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


class BecomeAdmin(django.db.models.Model):
    grade = django.db.models.IntegerField(choices=GRADE_CHOICES)
    letter = django.db.models.CharField(choices=LETTER_CHOICES)
    group = django.db.models.CharField(choices=((1, 1), (2, 2)))
    first_name = django.db.models.CharField()
    last_name = django.db.models.CharField()
    telegram_id = django.db.models.CharField()
