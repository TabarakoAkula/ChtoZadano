from django.contrib import admin
from django.utils.html import mark_safe

from homework.models import File, Homework, Image, Todo
from homework.utils import get_name_from_abbreviation


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = (
        "grade",
        "letter",
        "group",
        "subject_name",
        "short_description",
        "author",
        "created_at",
    )
    ordering = (
        "-created_at",
        "group",
    )
    search_fields = (
        "grade",
        "letter",
        "subject",
    )
    readonly_fields = ("created_at",)

    def short_description(self, obj):
        return obj.description[:50]

    def subject_name(self, obj):
        return get_name_from_abbreviation(obj.subject)

    short_description.short_description = "Описание"
    subject_name.short_description = "Предмет"


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "grade",
        "letter",
        "group",
        "subject",
        "get_small_img",
        "created_at",
    )
    fields = (
        "image",
        "get_big_img",
        "homework",
        "created_at",
    )
    readonly_fields = (
        "get_big_img",
        "created_at",
    )

    def get_small_img(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' width=100>")

    def get_big_img(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' width=500>")

    def grade(self, obj):
        return obj.homework.grade

    def letter(self, obj):
        return obj.homework.letter

    def group(self, obj):
        return obj.homework.group

    def subject(self, obj):
        return get_name_from_abbreviation(obj.homework.subject)

    def created_at(self, obj):
        return obj.homework.created_at

    grade.short_description = "Класс"
    letter.short_description = "Литера"
    group.short_description = "Группа"
    subject.short_description = "Предмет"
    get_small_img.short_description = "Изображение"
    get_big_img.short_description = "Изображение"
    created_at.short_description = "Дата создания"


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "grade",
        "letter",
        "group",
        "subject",
        "created_at",
    )
    fields = (
        "file",
        "homework",
        "created_at",
    )
    readonly_fields = ("created_at",)

    def grade(self, obj):
        return obj.homework.grade

    def letter(self, obj):
        return obj.homework.letter

    def group(self, obj):
        return obj.homework.group

    def subject(self, obj):
        return get_name_from_abbreviation(obj.homework.subject)

    def created_at(self, obj):
        return obj.homework.created_at

    grade.short_description = "Класс"
    letter.short_description = "Литера"
    group.short_description = "Группа"
    subject.short_description = "Предмет"
    created_at.short_description = "Дата создания"


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = (
        "get_homework_id",
        "get_user",
        "get_homework_grade",
        "get_homework_letter",
        "is_done",
        "created_at",
    )
    readonly_fields = ("created_at",)
    fields = (
        "is_done",
        "created_at",
    )

    def get_homework_grade(self, obj):
        return obj.homework_todo.first().grade

    def get_homework_letter(self, obj):
        return obj.homework_todo.first().letter

    def get_homework_id(self, obj):
        return obj.homework_todo.first().id

    def get_user(self, obj):
        return obj.user_todo.first().user

    get_user.short_description = "Пользователь"
    get_homework_grade.short_description = "Класс"
    get_homework_letter.short_description = "Литера"
    get_homework_id.short_description = "Id домашки"
