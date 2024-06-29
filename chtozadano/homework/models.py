from django.db import models


class Image(models.Model):
    image_path = models.ImageField(upload_to="img/homework/")


class Homework(models.Model):
    grade = models.IntegerField()
    letter = models.CharField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ManyToManyField(Image, blank=True)

    def __str__(self):
        return f"{self.grade}-{self.letter} | {self.description[:20]}"
