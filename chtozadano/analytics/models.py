from django.db import models

from homework.models import DateTimeWithoutTZField


class HomeworkAnalytics(models.Model):
    homeworks_add_site = models.IntegerField(default=0)
    homeworks_edit_site = models.IntegerField(default=0)
    homeworks_delete_site = models.IntegerField(default=0)
    homeworks_add_bot = models.IntegerField(default=0)
    homeworks_edit_bot = models.IntegerField(default=0)
    homeworks_delete_bot = models.IntegerField(default=0)
    active_class_name = models.CharField(null=True, blank=True)
    active_class_homeworks = models.IntegerField(default=0)
    cron_homeworks_deleted = models.IntegerField(default=0)
    cron_todo_deleted = models.IntegerField(default=0)
    created_at = DateTimeWithoutTZField(auto_now_add=True)


class UsersAnalytics(models.Model):
    new_users_site = models.IntegerField(default=0)
    new_users_bot = models.IntegerField(default=0)
    new_code_verifications = models.IntegerField(default=0)
    created_at = DateTimeWithoutTZField(auto_now_add=True)
