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
    ("Г", "В"),
)


class Homework(models.Model):
    grade = models.IntegerField(choices=GRADE_CHOICES)
    letter = models.CharField(choices=LETTER_CHOICES)
    description = models.TextField(null=True, blank=True)
    subject = models.CharField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.grade}-{self.letter} | {self.description[:20]}"


class Image(models.Model):
    image = models.ImageField(upload_to="img/homework/%Y/%d-%m/", null=True)
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
    )


class File(models.Model):
    file = models.FileField(upload_to="files/homework/%Y/%d-%m/", null=True)
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="files",
        null=True,
    )
    file_name = models.CharField()
