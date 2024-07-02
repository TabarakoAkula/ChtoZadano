import datetime
import os

from django.conf import settings
import django.contrib.auth
import django.db.utils
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.views import APIView

from users.forms import SignInForm, SignUpForm
from users.models import SignIn, User
from users.utils import confirmation_code_expired, create_password


class CodeConfirmationApi(APIView):
    def post(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        confirmation_code = request.data["confirmation_code"]
        user_name = request.data["name"]
        SignIn.objects.create(
            telegram_id=telegram_id,
            confirmation_code=confirmation_code,
            name=user_name,
        )
        return HttpResponse(
            f"Информация о пользователе {telegram_id}"
            f" успешно внесена в таблицу SignIN",
        )


class SignUpPage(View):
    def get(self, request):
        return render(
            request,
            "users/sign_up.html",
            context={"form": SignUpForm},
        )

    def post(self, request):
        code = request.POST["confirmation_code"]
        my_sign_in = SignIn.objects.filter(confirmation_code=code).first()
        try:
            database_datetime = my_sign_in.created_at.replace(
                tzinfo=None,
            ) + datetime.timedelta(hours=3)
        except AttributeError:
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                    "errors": ("Error: Bad code",),
                },
            )

        if confirmation_code_expired(database_datetime):
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                    "errors": ("Error: Code expired",),
                },
            )
        telegram_id = my_sign_in.telegram_id
        all_users = User.objects.filter(telegram_id=telegram_id).all()
        if all_users:
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                    "errors": ("Error: User already exist",),
                },
            )
        name = my_sign_in.name
        django_user = django.contrib.auth.models.User.objects.create_user(
            username=name,
            first_name=name,
            password=create_password(telegram_id, os.getenv("SECRET_KEY")),
        )
        User.objects.create(
            user=django_user,
            grade=request.POST["grade"],
            letter=request.POST["letter"],
            telegram_id=telegram_id,
        )
        django.contrib.auth.login(request, django_user)
        return redirect("users:account_page")


class SignInPage(View):
    def get(self, request):
        return render(
            request,
            "users/sign_in.html",
            context={"form": SignInForm},
        )

    def post(self, request):
        my_sign_in = SignIn.objects.filter(
            confirmation_code=request.POST["confirmation_code"],
        ).first()
        try:
            database_datetime = my_sign_in.created_at.replace(
                tzinfo=None,
            ) + datetime.timedelta(hours=3)
        except AttributeError:
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                    "errors": ("Error: Bad code",),
                },
            )
        if confirmation_code_expired(database_datetime):
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                    "errors": ("Error: Code expired",),
                },
            )
        telegram_id = my_sign_in.telegram_id
        all_users = User.objects.filter(telegram_id=telegram_id).all()
        if all_users:
            django_user = User.objects.get(telegram_id=telegram_id).user
        else:
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                    "errors": ("Error: Account with this id does not exist",),
                },
            )
        django.contrib.auth.login(request, django_user)
        return redirect("users:account_page")


class AccountPage(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("mainpage")
        return render(
            request,
            template_name="users/account.html",
            context={"user": User.objects.get(user=request.user)},
        )


class Logout(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("mainpage")
        django.contrib.auth.logout(request)
        return redirect("mainpage")
