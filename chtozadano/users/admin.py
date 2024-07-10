from django.contrib import admin

from users.models import SignIn, User


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
