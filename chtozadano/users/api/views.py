import asyncio
import json
import os

import django.contrib.auth
import django.db.utils
from django.http import HttpResponse
from rest_framework import response, viewsets
from rest_framework.views import APIView

from homework.utils import get_group_from_teacher
from users.api.serializers import (
    BecomeAdminSerializer,
    DefaultUserNameSerializer,
    UserSerializer,
)
from users.models import BecomeAdmin, SignIn, User
from users.utils import (
    become_admin_decision_notify,
    create_password,
    get_randomized_name,
    get_user_teachers,
    new_become_admin_notify,
)


class CodeConfirmationAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            confirmation_code = request.data["confirmation_code"]
            user_name = request.data["name"]
        except KeyError:
            return response.Response({"error": "Bad request data"}, status=400)
        SignIn.objects.create(
            telegram_id=telegram_id,
            confirmation_code=confirmation_code,
            name=user_name,
        )
        return response.Response(
            {
                "success": f"Информация о пользователе {telegram_id}"
                f" успешно внесена в таблицу SignIN",
            },
        )


class CreateUserAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            all_users = User.objects.filter(telegram_id=telegram_id).all()
            group = request.data["group"]
            grade = request.data["grade"]
            letter = request.data["letter"]
            name = request.data["name"]
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if not isinstance(group, int):
            group = get_group_from_teacher(
                group.replace("_", " "),
                grade,
                letter,
            )
            if group == 0:
                return response.Response(
                    {"error": "Bad teacher data"},
                    status=400,
                )
        if all_users:
            user = all_users[0]
            user.grade = grade
            user.letter = letter
            user.group = group
            user.save()
            return response.Response({"success": "Successful"})
        try:
            django_user = django.contrib.auth.models.User.objects.create_user(
                username=name,
                first_name=name,
                password=create_password(telegram_id, os.getenv("SECRET_KEY")),
            )
        except django.db.utils.IntegrityError:
            name = get_randomized_name(name)
            django_user = django.contrib.auth.models.User.objects.create_user(
                username=name,
                first_name=name,
                password=create_password(telegram_id, os.getenv("SECRET_KEY")),
            )
        User.objects.create(
            user=django_user,
            grade=grade,
            letter=letter,
            group=group,
            telegram_id=telegram_id,
        )
        return response.Response({"success": "Successful"})


class GetContactsAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = DefaultUserNameSerializer

    def get_contacts(self, request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        django_user = user_obj.user
        return response.Response(self.get_serializer(django_user).data)


class ChangeContactsAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
            django_user = user_obj.user
            first_name = request.data["first_name"]
            last_name = request.data["last_name"]
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        django_user.first_name = first_name
        django_user.last_name = last_name
        django_user.save()
        return response.Response({"success": "Successful"})


class GetQuotesAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"quotes_status": user_obj.show_quotes})


class ChangeQuotesAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        user_obj.show_quotes = not user_obj.show_quotes
        user_obj.save()
        return response.Response({"quotes_status": user_obj.show_quotes})


class ChangeGradeLetterAPI(APIView):
    @staticmethod
    def post(request):
        if request.user.is_staff and not request.user.is_superuser:
            return response.Response({"error": "Not allowed"}, status=403)
        try:
            telegram_id = request.data["telegram_id"]
            grade = request.data["grade"]
            letter = request.data["letter"]
            group = request.data["group"]
            user_obj = User.objects.get(telegram_id=telegram_id)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if not isinstance(group, int):
            group = get_group_from_teacher(
                group.replace("_", " "),
                grade,
                letter,
            )
            if group == 0:
                return response.Response(
                    {"error": "Bad teacher data"},
                    status=400,
                )
        user_obj.grade = grade
        user_obj.letter = letter
        user_obj.group = group
        user_obj.save()
        return response.Response({"success": "Successful"})


class GetChatModeAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"chat_mode": user_obj.chat_mode})


class ChangeChatModeAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        user_obj.chat_mode = not user_obj.chat_mode
        user_obj.save()
        return response.Response({"success": "Successful"})


class ShowBecomeAdminAPI(APIView):
    @staticmethod
    def post(request):
        try:
            if User.objects.get(
                telegram_id=request.data["telegram_id"],
            ).user.is_superuser:
                request_data = BecomeAdmin.objects.all()
                serialized_data = BecomeAdminSerializer(
                    request_data,
                    many=True,
                ).data
                return response.Response(serialized_data)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"error": "Not allowed"}, status=403)


class BecomeAdminAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
            django_user = user_obj.user
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if django_user.is_staff:
            return response.Response(
                {"error": "You are already admin"},
                status=403,
            )
        if django_user.is_superuser:
            return response.Response({"error": "You are superuser, damn"})
        try:
            BecomeAdmin.objects.get(telegram_id=telegram_id)
        except BecomeAdmin.MultipleObjectsReturned:
            return response.Response(
                {"error": "Already have request"},
                status=403,
            )
        except BecomeAdmin.DoesNotExist:
            BecomeAdmin.objects.create(
                grade=user_obj.grade,
                letter=user_obj.letter,
                first_name=django_user.first_name,
                last_name=django_user.last_name,
                group=user_obj.group,
                telegram_id=telegram_id,
            )
            asyncio.run(new_become_admin_notify())
            return response.Response({"success": "Successful"})
        return response.Response({"error": "Wait pls"})


class AcceptDeclineBecomeAdminAPI(APIView):
    @staticmethod
    def post(request):
        try:
            if User.objects.get(
                telegram_id=request.data["telegram_id"],
            ).user.is_superuser:
                candidate_id = request.data["candidate_id"]
                try:
                    BecomeAdmin.objects.get(telegram_id=candidate_id)
                except BecomeAdmin.DoesNotExist:
                    return response.Response(
                        {"error": "Это кто? Я такого не знаю"},
                        status=400,
                    )
                decision = request.data["decision"]
                if decision == "accept":
                    candidat_user = User.objects.get(
                        telegram_id=candidate_id,
                    ).user
                    candidat_user.is_staff = True
                    candidat_user.save()
                    BecomeAdmin.objects.get(telegram_id=candidate_id).delete()
                    asyncio.run(
                        become_admin_decision_notify(candidate_id, True),
                    )
                    return response.Response(
                        {"success": "Successful accepted"},
                    )
                if decision == "decline":
                    BecomeAdmin.objects.get(telegram_id=candidate_id).delete()
                    asyncio.run(
                        become_admin_decision_notify(candidate_id, False),
                    )
                    return response.Response(
                        {"success": "Successful declined"},
                    )
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"error": "Not allowed"}, status=403)


class IsUserInSystemAPI(APIView):
    @staticmethod
    def post(request):
        try:
            if User.objects.filter(
                telegram_id=request.data["telegram_id"],
            ).first():
                return HttpResponse(True)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return HttpResponse(False)


class DeleteUserBecomeAdminAPI(APIView):
    @staticmethod
    def post(request):
        try:
            become_admin_obj = BecomeAdmin.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            become_admin_obj.delete()
        except BecomeAdmin.DoesNotExist:
            pass
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"success": "OK"})


class GetAdminsAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_admins(self, request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = User.objects.get(telegram_id=telegram_id)
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, 400)
        admins = User.objects.filter(
            grade=user_obj.grade,
            letter=user_obj.letter,
            user__is_staff=True,
        ).all()
        serialized = self.get_serializer(admins, many=True)
        return response.Response(serialized.data)


class IsUserAdminAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = User.objects.filter(
                telegram_id=request.data["telegram_id"],
            ).first()
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if user_obj:
            return response.Response(
                json.dumps(
                    {
                        "is_admin": user_obj.user.is_staff,
                        "is_superuser": user_obj.user.is_superuser,
                    },
                ),
            )
        return response.Response({"error": "User does not exist"}, status=400)


class GetUserEngTeachersAPI(APIView):
    @staticmethod
    def post(request):
        try:
            grade = request.data["grade"]
            letter = request.data["letter"]
        except (KeyError, User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        teachers = get_user_teachers(grade, letter)
        if teachers:
            return response.Response({"teachers": teachers})
        return response.Response({"error": "Unknown grade|letter"}, status=400)


class GetFastAddAPI(APIView):
    @staticmethod
    def post(request):
        telegram_id = request.data["telegram_id"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        return response.Response({"fast_hw": user_obj.fast_hw})


class ChangeFastAddAPI(APIView):
    @staticmethod
    def post(request):
        telegram_id = request.data["telegram_id"]
        user_obj = User.objects.get(telegram_id=telegram_id)
        user_obj.fast_hw = not user_obj.fast_hw
        user_obj.save()
        return response.Response({"success": "Successful"})
