import asyncio
import datetime
import os
from random import random

from django.contrib import messages
import django.contrib.auth
from django.contrib.auth.base_user import check_password
import django.db.utils
from django.shortcuts import redirect, render
from django.views import View

from users.forms import (
    ChangeContactsForm,
    SignInForm,
    SignInPasswordForm,
    SignUpForm,
    SignUpPasswordForm,
)
from users.models import BecomeAdmin, SignIn, User
from users.utils import (
    become_admin_decision_notify,
    confirmation_code_expired,
    create_password,
    new_become_admin_notify,
    validate_password,
)


class SignUpPage(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        return render(
            request,
            "users/sign_up.html",
            context={"form": SignUpForm},
        )

    @staticmethod
    def post(request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        code = request.POST["confirmation_code"]
        my_sign_in = SignIn.objects.filter(confirmation_code=code).first()
        try:
            database_datetime = my_sign_in.created_at.replace(
                tzinfo=None,
            ) + datetime.timedelta(hours=3)
        except AttributeError:
            messages.error(request, "Неправильный код")
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                },
            )

        if confirmation_code_expired(database_datetime):
            messages.error(request, "Время действия кода истекло")
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                },
            )
        telegram_id = my_sign_in.telegram_id
        all_users = User.objects.filter(telegram_id=telegram_id).all()
        if all_users:
            messages.error(
                request,
                "Пользователь с таким telegram аккаунтом уже существует",
            )
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                },
            )
        name = my_sign_in.name
        try:
            django_user = django.contrib.auth.models.User.objects.create_user(
                username=name,
                first_name=name,
                password=create_password(telegram_id, os.getenv("SECRET_KEY")),
            )
        except django.db.utils.IntegrityError:
            django_user = django.contrib.auth.models.User.objects.create_user(
                username=name + str(random.getrandbits(128))[:15],
                first_name=name,
                password=create_password(telegram_id, os.getenv("SECRET_KEY")),
            )
        User.objects.create(
            user=django_user,
            grade=request.POST["grade"],
            letter=request.POST["letter"],
            group=request.POST["group"],
            telegram_id=telegram_id,
        )
        django.contrib.auth.login(request, django_user)
        my_sign_in.delete()
        messages.success(request, "Аккаунт успешно создан")
        return redirect("users:account_page")


class SignUpPasswordPage(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        return render(
            request,
            "users/sign_up_password.html",
            context={"form": SignUpPasswordForm},
        )

    @staticmethod
    def post(request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        form = SignUpPasswordForm(request.POST).data
        password = form["password"]
        password_checker = validate_password(password)
        if not password_checker[0]:
            messages.error(request, password_checker[1])
            return render(
                request,
                "users/sign_up_password.html",
                context={
                    "form": SignUpPasswordForm(request.POST),
                },
            )
        if password != form["repeat_password"]:
            messages.error(request, "Введенные пароли не совпадают")
            return render(
                request,
                "users/sign_up_password.html",
                context={
                    "form": SignUpPasswordForm(request.POST),
                },
            )
        try:
            django.contrib.auth.models.User.objects.get(
                username=form["username"],
            )
        except django.contrib.auth.models.User.DoesNotExist:
            django_user = django.contrib.auth.models.User.objects.create_user(
                username=form["username"],
                password=form["password"],
                first_name=form["username"],
            )
            User.objects.create(
                user=django_user,
                grade=request.POST["grade"],
                letter=request.POST["letter"],
                group=request.POST["group"],
            )
            django.contrib.auth.login(request, django_user)
            messages.success(request, "Аккаунт успешно создан")
            return redirect("users:account_page")
        else:
            messages.error(request, "Выберите другой логин")
            return render(
                request,
                "users/sign_up_password.html",
                context={
                    "form": SignUpPasswordForm(request.POST),
                },
            )


class SignInPage(View):
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return render(
                request,
                "users/sign_in.html",
                context={"form": SignInForm},
            )
        messages.error(request, "Вы уже вошли в аккаунт")
        return redirect("users:account_page")

    @staticmethod
    def post(request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        my_sign_in = SignIn.objects.filter(
            confirmation_code=request.POST["confirmation_code"],
        ).first()
        try:
            database_datetime = my_sign_in.created_at.replace(
                tzinfo=None,
            ) + datetime.timedelta(hours=3)
        except AttributeError:
            messages.error(request, "Неправильный код")
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                },
            )
        if confirmation_code_expired(database_datetime):
            messages.error(request, "Время действия кода истекло")
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                },
            )
        telegram_id = my_sign_in.telegram_id
        all_users = User.objects.filter(telegram_id=telegram_id).all()
        if all_users:
            django_user = User.objects.get(telegram_id=telegram_id).user
        else:
            messages.error(
                request,
                "Аккаунт с таким telegram аккаунтом уже существует",
            )
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                },
            )
        django.contrib.auth.login(request, django_user)
        my_sign_in.delete()
        messages.success(request, "Вы успешно вошли в аккаунт")
        return redirect("users:account_page")


class SignInPasswordPage(View):
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return render(
                request,
                "users/sign_in_password.html",
                context={"form": SignInPasswordForm},
            )
        messages.error(request, "Вы уже вошли в аккаунт")
        return redirect("users:account_page")

    @staticmethod
    def post(request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        form = SignInPasswordForm(request.POST).data
        try:
            django_user = django.contrib.auth.models.User.objects.get(
                username=form["username"],
            )
        except django.contrib.auth.models.User.DoesNotExist:
            messages.error(request, "Неправильный логин или пароль")
            return render(
                request,
                "users/sign_in_password.html",
                context={
                    "form": SignInPasswordForm(request.POST),
                },
            )
        if check_password(form["password"], django_user.password):
            django.contrib.auth.login(request, django_user)
            messages.success(request, "Вы успешно вошли в аккаунт")
            return redirect("users:account_page")
        messages.error(request, "Неправильный логин или пароль")
        return render(
            request,
            "users/sign_in_password.html",
            context={
                "form": SignInPasswordForm(request.POST),
            },
        )


class AccountPage(View):
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("users:signin_page")
        show_admin = False
        try:
            BecomeAdmin.objects.get(
                telegram_id=request.user.server_user.telegram_id,
            )
        except BecomeAdmin.DoesNotExist:
            show_admin = True
        return render(
            request,
            template_name="users/account.html",
            context={
                "user": User.objects.get(user=request.user),
                "show_admin": show_admin,
            },
        )


class Logout(View):
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("users:signin_page")
        django.contrib.auth.logout(request)
        messages.success(request, "Вы вышли из аккаунта")
        return redirect("mainpage")


class ChangeContactsPage(View):
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("users:signin_page")
        return render(
            request,
            "users/change_contacts.html",
            context={"form": ChangeContactsForm},
        )

    @staticmethod
    def post(request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("users:signin_page")
        form = ChangeContactsForm(request.POST).data
        django_user = request.user
        django_user.first_name = form["first_name"]
        django_user.last_name = form["last_name"]
        django_user.save()
        messages.success(request, "Данные обновлены")
        return redirect("users:account_page")


class BecomeAdminPage(View):
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("users:signin_page")
        if request.user.is_staff:
            messages.error(request, "Вы уже имеете роль администратора")
            return redirect("homework:homework_page")
        if not request.user.server_user.telegram_id:
            messages.error(
                request,
                "Необходим аккаунт c привязанным"
                " telegram_id для этого действия",
            )
            return redirect("users:account_page")
        try:
            BecomeAdmin.objects.get(
                telegram_id=request.user.server_user.telegram_id,
            )
        except BecomeAdmin.DoesNotExist:
            return render(request, "users/become_admin.html")
        messages.error(request, "Вы уже подавали заявку, ожидайте")
        return redirect("users:account_page")

    @staticmethod
    def post(request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("users:signin_page")
        if request.user.is_staff:
            messages.error(request, "Вы уже имеете роль администратора")
            return redirect("homework:homework_page")
        if not request.user.server_user.telegram_id:
            messages.error(
                request,
                "Необходим аккаунт c привязанным"
                " telegram_id для этого действия",
            )
            return redirect("users:account_page")
        first_name, last_name = (
            request.POST["first_name"],
            request.POST["last_name"],
        )
        user_obj = request.user.server_user
        BecomeAdmin.objects.create(
            grade=user_obj.grade,
            letter=user_obj.letter,
            first_name=first_name,
            last_name=last_name,
            group=user_obj.group,
            telegram_id=user_obj.telegram_id,
        )
        messages.success(request, "Заявка успешно отправлена")
        asyncio.run(new_become_admin_notify())
        return redirect("users:account_page")


class ShowBecomeAdmin(View):
    @staticmethod
    def get(request):
        if request.user.is_superuser:
            data = BecomeAdmin.objects.all()
            return render(
                request,
                "users/show_become_admin.html",
                context={"data": data},
            )
        messages.error(request, "У вас недостаточно прав для этого действия")
        return redirect("users:account_page")


class BecomeAdminAccept(View):
    @staticmethod
    def get(request, telegram_id):
        if request.user.is_superuser:
            BecomeAdmin.objects.get(telegram_id=telegram_id).delete()
            user_obj = User.objects.get(telegram_id=telegram_id).user
            user_obj.is_staff = True
            user_obj.save()
            messages.success(
                request,
                f"Пользователь {user_obj.first_name}"
                f" {user_obj.last_name} назначен администратором",
            )
            asyncio.run(become_admin_decision_notify(telegram_id, True))
            return redirect("users:show_become_admin")
        messages.error(request, "У вас недостаточно прав для этого действия")
        return redirect("users:account_page")


class BecomeAdminDecline(View):
    @staticmethod
    def get(request, telegram_id):
        if request.user.is_superuser:
            BecomeAdmin.objects.get(telegram_id=telegram_id).delete()
            messages.success(
                request,
                f"Заявка пользователя {request.user.first_name}"
                f" {request.user.last_name} отклонена",
            )
            asyncio.run(become_admin_decision_notify(telegram_id, False))
            return redirect("users:show_become_admin")
        messages.error(request, "У вас недостаточно прав для этого действия")
        return redirect("users:account_page")
