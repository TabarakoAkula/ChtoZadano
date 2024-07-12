from django.db import models


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
    ("Г", "В"),
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
    todo = models.ManyToManyField(Todo, related_name="homework_todo")

    def __str__(self):
        return f"{self.grade}{self.letter} - {self.subject}"

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"


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

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
