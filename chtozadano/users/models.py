from django.contrib.auth import get_user_model
import django.db.models

import homework.models

DjangoUser = get_user_model()

GRADE_CHOICES = (
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
    ("В", "В"),
    ("Г", "Г"),
)


class DateTimeWithoutTZField(django.db.models.DateTimeField):
    def db_type(self, connection):
        return "timestamp"


class UsersManager(django.db.models.Manager):
    def mode_toggle_data(self):
        return self.aggregate(
            total_users=django.db.models.Count("pk"),
            chat_mode_enable=django.db.models.Count(
                "pk",
                filter=django.db.models.Q(chat_mode=True),
            ),
            hast_hw_enable=django.db.models.Count(
                "pk",
                filter=django.db.models.Q(fast_hw=True),
            ),
            show_quotes_enable=django.db.models.Count(
                "pk",
                filter=django.db.models.Q(show_quotes=True),
            ),
        )


class User(django.db.models.Model):
    user = django.db.models.OneToOneField(
        DjangoUser,
        on_delete=django.db.models.CASCADE,
        primary_key=True,
        related_name="server_user",
        verbose_name="Пользователь",
    )
    grade = django.db.models.IntegerField(
        choices=GRADE_CHOICES,
        verbose_name="Класс",
    )
    letter = django.db.models.CharField(
        choices=LETTER_CHOICES,
        verbose_name="Буква",
    )
    telegram_id = django.db.models.CharField(
        null=True,
        blank=True,
        verbose_name="Телеграм id",
    )
    group = django.db.models.IntegerField(
        choices=((1, 1), (2, 2)),
        default=1,
        verbose_name="Группа",
    )
    chat_mode = django.db.models.BooleanField(
        default=True,
        verbose_name="Режим чата",
    )
    show_quotes = django.db.models.BooleanField(
        default=True,
        verbose_name="Режим цитат",
    )
    fast_hw = django.db.models.BooleanField(
        default=True,
        verbose_name="Режим быстрого добавления дз",
    )
    todo = django.db.models.ManyToManyField(
        homework.models.Todo,
        blank=True,
        related_name="user_todo",
    )
    send_cleaner = django.db.models.BooleanField(
        default=False,
        verbose_name="Отправка очистки",
    )
    send_analytics = django.db.models.BooleanField(
        default=False,
        verbose_name="Отправка аналитики",
    )
    objects = django.db.models.Manager()
    analytics = UsersManager()

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            django.db.models.Index(fields=["grade", "letter"]),
        ]


class SignIn(django.db.models.Model):
    singning_user = django.db.models.OneToOneField(
        User,
        on_delete=django.db.models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    telegram_id = django.db.models.CharField(
        null=True,
        blank=True,
        verbose_name="Telegram ID",
    )
    confirmation_code = django.db.models.CharField(
        null=True,
        blank=True,
        verbose_name="Код идентификации",
    )
    created_at = DateTimeWithoutTZField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    name = django.db.models.CharField(
        null=True,
        blank=True,
        verbose_name="Имя",
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Идентификация"
        verbose_name_plural = "Идентификации"


class BecomeAdmin(django.db.models.Model):
    grade = django.db.models.IntegerField(
        choices=GRADE_CHOICES,
        verbose_name="Класс",
    )
    letter = django.db.models.CharField(
        choices=LETTER_CHOICES,
        verbose_name="Литера",
    )
    group = django.db.models.IntegerField(
        choices=((1, 1), (2, 2)),
        verbose_name="Группа",
    )
    first_name = django.db.models.CharField(
        verbose_name="Имя",
    )
    last_name = django.db.models.CharField(
        verbose_name="Фамилия",
    )
    telegram_id = django.db.models.CharField(
        null=True,
        blank=True,
        verbose_name="Телеграм id",
    )
    created_at = DateTimeWithoutTZField(
        auto_now_add=True,
        verbose_name="Дата создания",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.telegram_id)

    class Meta:
        verbose_name = "Заявка на администратора"
        verbose_name_plural = "Заявки на администратора"
