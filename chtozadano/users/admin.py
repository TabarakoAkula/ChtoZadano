from django.contrib import admin

from users.models import SignIn, Todo, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "grade",
        "letter",
        "group",
        "user",
        "telegram_id",
        "chat_mode",
    )
    search_fields = (
        "grade",
        "letter",
        "group",
        "user",
        "telegram_id",
    )


@admin.register(SignIn)
class SignInAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "telegram_id",
        "confirmation_code",
        "created_at",
    )
    search_fields = (
        "telegram_id",
        "name",
    )


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = (
        "get_user",
        "get_homework",
        "is_done",
    )

    def get_user(self, obj):
        return obj.user

    def get_homework(self, obj):
        return obj.homework

    get_user.short_description = "Пользователь"
    get_homework.short_description = "Домашнее задание"
