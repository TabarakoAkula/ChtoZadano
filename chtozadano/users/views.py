import datetime
import json
import os

from django.conf import settings
from django.contrib import messages
import django.contrib.auth
from django.contrib.auth.base_user import check_password
import django.db.utils
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.views import APIView

from users.forms import (
    ChangeContactsForm,
    EditNotebookForm,
    SignInForm,
    SignInPasswordForm,
    SignUpForm,
    SignUpPasswordForm,
)
from users.models import BecomeAdmin, SignIn, User
from users.serializers import BecomeAdminSerializer
from users.utils import (
    confirmation_code_expired,
    create_password,
    validate_password,
)


class CodeConfirmationAPI(APIView):
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
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        return render(
            request,
            "users/sign_up.html",
            context={"form": SignUpForm},
        )

    def post(self, request):
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
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                    "errors": ("Неправильный код",),
                },
            )

        if confirmation_code_expired(database_datetime):
            return render(
                request,
                "users/sign_up.html",
                context={
                    "form": SignUpForm(request.POST),
                    "errors": ("Время действия кода истекло",),
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
                    "errors": ("Пользователь уже существует",),
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
            group=request.POST["group"],
            telegram_id=telegram_id,
        )
        django.contrib.auth.login(request, django_user)
        my_sign_in.delete()
        messages.success(request, "Аккаунт успешно создан")
        return redirect("users:account_page")


class SignInPage(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(
                request,
                "users/sign_in.html",
                context={"form": SignInForm},
            )
        messages.error(request, "Вы уже вошли в аккаунт")
        return redirect("users:account_page")

    def post(self, request):
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
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                    "errors": ("Неправильный код",),
                },
            )
        if confirmation_code_expired(database_datetime):
            return render(
                request,
                "users/sign_in.html",
                context={
                    "form": SignInForm(request.POST),
                    "errors": ("Время действия кода истекло",),
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
                    "errors": (
                        "Аккаунт с таким telegram аккаунтов уже существует",
                    ),
                },
            )
        django.contrib.auth.login(request, django_user)
        my_sign_in.delete()
        messages.success(request, "Вы успешно вошли в аккаунт")
        return redirect("users:account_page")


class SignUpPasswordPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        return render(
            request,
            "users/sign_up_password.html",
            context={"form": SignUpPasswordForm},
        )

    def post(self, request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        form = SignUpPasswordForm(request.POST).data
        password = form["password"]
        password_checker = validate_password(password)
        if not password_checker[0]:
            return render(
                request,
                "users/sign_up_password.html",
                context={
                    "form": SignUpPasswordForm(request.POST),
                    "errors": (password_checker[1],),
                },
            )
        if password != form["repeat_password"]:
            return render(
                request,
                "users/sign_up_password.html",
                context={
                    "form": SignUpPasswordForm(request.POST),
                    "errors": ("Введенные пароли не совпадают",),
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
            return render(
                request,
                "users/sign_up_password.html",
                context={
                    "form": SignUpPasswordForm(request.POST),
                    "errors": ("Выберите другой логин",),
                },
            )


class SignInPasswordPage(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(
                request,
                "users/sign_in_password.html",
                context={"form": SignInPasswordForm},
            )
        messages.error(request, "Вы уже вошли в аккаунт")
        return redirect("users:account_page")

    def post(self, request):
        if request.user.is_authenticated:
            messages.error(request, "Вы уже вошли в аккаунт")
            return redirect("users:account_page")
        form = SignInPasswordForm(request.POST).data
        try:
            django_user = django.contrib.auth.models.User.objects.get(
                username=form["username"],
            )
        except django.contrib.auth.models.User.DoesNotExist:
            return render(
                request,
                "users/sign_in_password.html",
                context={
                    "form": SignInPasswordForm(request.POST),
                    "errors": ("Неправильный логин или пароль",),
                },
            )
        if check_password(form["password"], django_user.password):
            django.contrib.auth.login(request, django_user)
            messages.success(request, "Вы успешно вошли в аккаунт")
            return redirect("users:account_page")
        return render(
            request,
            "users/sign_in_password.html",
            context={
                "form": SignInPasswordForm(request.POST),
                "errors": ("Неправильный логин или пароль",),
            },
        )


class AccountPage(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
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
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
        django.contrib.auth.logout(request)
        messages.success(request, "Вы вышли из аккаунта")
        return redirect("mainpage")


class BecomeAdminPage(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
        if request.user.is_staff:
            messages.error(request, "Вы уже имеете роль администратора")
            return redirect("homework:homework_page")
        try:
            BecomeAdmin.objects.get(
                telegram_id=request.user.server_user.telegram_id,
            )
        except BecomeAdmin.DoesNotExist:
            return render(request, "users/become_admin.html")
        messages.error(request, "Вы уже подавали заявку, ожидайте")
        return redirect("users:account_page")

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
        if request.user.is_staff:
            messages.error(request, "Вы уже имеете роль администратора")
            return redirect("homework:homework_page")
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
        return redirect("users:account_page")


class ShowBecomeAdmin(View):
    def get(self, request):
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
    def get(self, request, telegram_id):
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
            return redirect("users:show_become_admin")
        messages.error(request, "У вас недостаточно прав для этого действия")
        return redirect("users:account_page")


class BecomeAdminDecline(View):
    def get(self, request, telegram_id):
        if request.user.is_superuser:
            BecomeAdmin.objects.get(telegram_id=telegram_id).delete()
            messages.success(
                request,
                f"Заявка пользователя {request.user.first_name}"
                f" {request.user.last_name} отклонена",
            )
            return redirect("users:show_become_admin")
        messages.error(request, "У вас недостаточно прав для этого действия")
        return redirect("users:account_page")


class ChangeContactsPage(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
        return render(
            request,
            "users/change_contacts.html",
            context={"form": ChangeContactsForm},
        )

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
        form = ChangeContactsForm(request.POST).data
        django_user = request.user
        django_user.first_name = form["first_name"]
        django_user.last_name = form["last_name"]
        django_user.save()
        messages.success(request, "Данные обновлены")
        return redirect("users:account_page")


class EditNotebook(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
        return render(
            request,
            "users/edit_notebook.html",
            context={"form": EditNotebookForm},
        )

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("mainpage")
        form = EditNotebookForm(request.POST).data
        user = User.objects.get(user=request.user)
        user.notebook = form["text"]
        user.notebook_color = form["color"]
        user.save()
        return redirect("users:account_page")


class BecomeAdminAPI(APIView):
    def get(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        if User.objects.get(
            telegram_id=request.data["telegram_id"],
        ).user.is_superuser:
            request_data = BecomeAdmin.objects.all()
            serialized_data = BecomeAdminSerializer(
                request_data,
                many=True,
            ).data
            return HttpResponse(json.dumps(serialized_data))
        return HttpResponse("Not allowed")

    def post(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        grade = request.data["grade"]
        letter = request.data["letter"]
        group = request.data["group"]
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        django_user = User.objects.get(telegram_id=telegram_id).user
        if django_user.is_staff:
            return HttpResponse("You are already admin")
        if django_user.is_superuser:
            return HttpResponse("You are superuser, damn")
        try:
            BecomeAdmin.objects.get(telegram_id=telegram_id)
        except BecomeAdmin.MultipleObjectsReturned:
            return HttpResponse("Already have request")
        except BecomeAdmin.DoesNotExist:
            BecomeAdmin.objects.create(
                grade=grade,
                letter=letter,
                first_name=first_name,
                last_name=last_name,
                group=group,
                telegram_id=telegram_id,
            )
            return HttpResponse("Successful")
        return HttpResponse("Wait pls")


class AcceptDeclineBecomeAdminAPI(APIView):
    def post(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        if User.objects.get(
            telegram_id=request.data["telegram_id"],
        ).user.is_superuser:
            candidate_id = request.data["candidate_id"]
            try:
                BecomeAdmin.objects.get(telegram_id=candidate_id)
            except BecomeAdmin.DoesNotExist:
                return HttpResponse("Это кто? Я такого не знаю")
            decision = request.data["decision"]
            if decision == "accept":
                candidat_user = User.objects.get(telegram_id=candidate_id).user
                candidat_user.is_staff = True
                candidat_user.save()
                BecomeAdmin.objects.get(telegram_id=candidate_id).delete()
                return HttpResponse("Successful accepted")
            if decision == "decline":
                BecomeAdmin.objects.get(telegram_id=candidate_id).delete()
                return HttpResponse("Successful declined")
        return HttpResponse("Not allowed")


class ChangeGradeLetterAPI(APIView):
    def post(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        if request.user.is_staff and not request.user.is_superuser:
            return HttpResponse("Not allowed")
        telegram_id = request.data["telegram_id"]
        grade = request.data["grade"]
        letter = request.data["letter"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        user_obj.grade = grade
        user_obj.letter = letter
        user_obj.save()
        return HttpResponse("Successful")


class ChangeChatModeAPI(APIView):
    def get(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        return HttpResponse(user_obj.chat_mode)

    def post(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        chat_mode = request.data["chat_mode"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        user_obj.chat_mode = chat_mode
        user_obj.save()
        return HttpResponse("Successful")


class ChangeContactsAPI(APIView):
    def get(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        return HttpResponse(
            json.dumps(
                {
                    "first_name": django_user.first_name,
                    "last_name": django_user.last_name,
                },
            ),
        )

    def post(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        django_user.first_name = first_name
        django_user.last_name = last_name
        django_user.save()
        return HttpResponse("Successful")
