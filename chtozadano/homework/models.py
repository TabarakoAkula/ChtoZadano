from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Homework(models.Model):
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(11)],
    )
    letter = models.CharField(max_length=1)
    description = models.TextField(null=True, blank=True)
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
