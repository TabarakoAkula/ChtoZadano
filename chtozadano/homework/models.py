from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Image(models.Model):
    image_path = models.ImageField(upload_to="img/homework/")


class Homework(models.Model):
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(11)],
    )
    letter = models.CharField(max_length=1)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ManyToManyField(Image, blank=True)

    def __str__(self):
        return f"{self.grade}-{self.letter} | {self.description[:20]}"
