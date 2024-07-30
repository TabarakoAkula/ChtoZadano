import json
import os

import django.contrib.auth
import django.db.utils
from django.http import HttpResponse
from rest_framework.views import APIView

from users.models import BecomeAdmin, SignIn, User
from users.serializers import BecomeAdminSerializer
from users.utils import (
    create_password,
)


class CodeConfirmationAPI(APIView):
    @staticmethod
    def post(request):
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


class CreateUserAPI(APIView):
    @staticmethod
    def post(request):
        telegram_id = request.data["telegram_id"]
        all_users = User.objects.filter(telegram_id=telegram_id).all()
        if all_users:
            return HttpResponse("Пользователь уже зарегистрирован")
        django_user = django.contrib.auth.models.User.objects.create_user(
            username=request.data["name"],
            first_name=request.data["name"],
            password=create_password(telegram_id, os.getenv("SECRET_KEY")),
        )
        User.objects.create(
            user=django_user,
            grade=request.data["grade"],
            letter=request.data["letter"],
            group=request.data["group"],
            telegram_id=telegram_id,
        )
        return HttpResponse("Successful")


class GetContactsAPI(APIView):
    @staticmethod
    def post(request):
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


class ChangeContactsAPI(APIView):
    @staticmethod
    def post(request):
        telegram_id = request.data["telegram_id"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        django_user.first_name = first_name
        django_user.last_name = last_name
        django_user.save()
        return HttpResponse("Successful")


class ChangeGradeLetterAPI(APIView):
    @staticmethod
    def post(request):
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


class GetChatModeAPI(APIView):
    @staticmethod
    def post(request):
        telegram_id = request.data["telegram_id"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        return HttpResponse(user_obj.chat_mode)


class ChangeChatModeAPI(APIView):
    @staticmethod
    def post(request):
        telegram_id = request.data["telegram_id"]
        chat_mode = request.data["chat_mode"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        user_obj.chat_mode = chat_mode
        user_obj.save()
        return HttpResponse("Successful")


class ShowBecomeAdminAPI(APIView):
    @staticmethod
    def post(request):
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


class BecomeAdminAPI(APIView):
    @staticmethod
    def post(request):
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
    @staticmethod
    def post(request):
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
