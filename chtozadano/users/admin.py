from django.contrib import admin
from django.utils.html import mark_safe

from users.models import BecomeAdmin, SignIn, User


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


@admin.register(BecomeAdmin)
class BecomeAdminAdmin(admin.ModelAdmin):
    list_display = (
        "grade",
        "letter",
        "group",
        "first_name",
        "last_name",
        "telegram",
    )

    search_fields = (
        "grade",
        "letter",
        "group",
        "first_name",
        "last_name",
    )

    def telegram(self, obj):
        return mark_safe(
            f"<a href='tg://openmessage?user_id={obj.telegram_id}'>Ссылка</a>",
        )

    telegram.short_description = "Телеграм"
