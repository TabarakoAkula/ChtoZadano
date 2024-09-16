from django.db import models
from django.db.models.functions import Length


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


class DateTimeWithoutTZField(models.DateTimeField):
    def db_type(self, connection):
        return "timestamp"


class Todo(models.Model):
    is_done = models.BooleanField(
        default=False,
        verbose_name="Выполнено",
    )
    created_at = DateTimeWithoutTZField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.created_at.strftime('%d-%m-%Y')}"

    class Meta:
        verbose_name = "Список ToDo"
        verbose_name_plural = "Списки ToDo"


class HomeworkManager(models.Manager):
    def get_average_text_length(self):
        return self.aggregate(
            average_text_lengt=models.Avg(Length("description")),
        )

    def get_average_media_number(self):
        attachments_account = self.annotate(
            attachment_count=models.Count("images"),
        )
        return {
            "total_media": attachments_account.count(),
            "without_media": attachments_account.filter(
                attachment_count__lte=0,
            ).count(),
            "few_media": attachments_account.filter(
                attachment_count__gte=1,
                attachment_count__lte=3,
            ).count(),
            "enougth_media": attachments_account.filter(
                attachment_count__gte=4,
            ).count(),
        }

    def get_average_time_add(self):
        return self.aggregate(
            total_homeworks=models.Count("pk"),
            morning=models.Count(
                "pk",
                filter=(
                    models.Q(created_at__hour__gte=8)
                    & models.Q(created_at__hour__lte=16)
                ),
            ),
            evening=models.Count(
                "pk",
                filter=(
                    models.Q(created_at__hour__gte=16)
                    & models.Q(created_at__hour__lte=24)
                ),
            ),
            night=models.Count(
                "pk",
                filter=(
                    models.Q(created_at__hour__gte=0)
                    & models.Q(created_at__hour__lte=8)
                ),
            ),
        )


class Homework(models.Model):
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        verbose_name="Класс",
    )
    letter = models.CharField(
        choices=LETTER_CHOICES,
        verbose_name="Литера",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание",
    )
    subject = models.CharField(
        null=True,
        verbose_name="Предмет",
    )
    group = models.IntegerField(
        choices=((-3, -3), (-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2)),
        default=0,
        verbose_name="Группа",
    )
    created_at = DateTimeWithoutTZField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    todo = models.ManyToManyField(
        Todo,
        related_name="homework_todo",
        blank=True,
    )
    author = models.CharField(default="Anonym", verbose_name="Автор")
    objects = models.Manager()
    analytics = HomeworkManager()

    def __str__(self):
        return f"{self.grade}{self.letter} - {self.subject}"

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        indexes = [
            models.Index(fields=["grade", "letter"]),
        ]


class Image(models.Model):
    image = models.ImageField(
        upload_to="img/homework/%Y/%d-%m/",
        null=True,
        verbose_name="Путь к изображению",
    )
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        verbose_name="Домашнее задание",
    )
    telegram_file_id = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.image.url

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


class File(models.Model):
    file = models.FileField(
        upload_to="files/homework/%Y/%d-%m/",
        null=True,
        verbose_name="Путь к файлу",
    )
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="files",
        null=True,
        verbose_name="Домашнее задание",
    )
    file_name = models.CharField(
        verbose_name="Название файлы",
    )
    telegram_file_id = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.file.url

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"


class Schedule(models.Model):
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        verbose_name="Класс",
    )
    letter = models.CharField(
        choices=LETTER_CHOICES,
        verbose_name="Литера",
    )
    group = models.IntegerField(verbose_name="Группа", default=1)
    weekday = models.IntegerField(verbose_name="День недели")
    lesson = models.IntegerField(verbose_name="Урок")
    subject = models.CharField(verbose_name="Предмет")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

    def __str__(self):
        return (
            f"{self.grade}{self.letter} {self.weekday}"
            f" {self.lesson} {self.subject}"
        )
