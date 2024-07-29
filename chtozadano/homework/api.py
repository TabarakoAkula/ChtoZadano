from datetime import datetime, timedelta
import json

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.views import APIView

from homework.models import File, Homework, Image, Todo
from homework.serializers import HomeworkSerializer
from homework.utils import (
    get_abbreviation_from_name,
    get_tomorrow_schedule,
    get_user_subjects_abbreviation,
)
import users.models


class GetLastHomeworkAllSubjectsAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        user = users.models.User.objects.get(
            telegram_id=request.data["telegram_id"],
        )
        grade = user.grade
        letter = user.letter
        group = user.group
        subjects = get_user_subjects_abbreviation(grade, letter)
        data = {}
        for subject in subjects:
            try:
                if user.user.is_staff or user.user.is_superuser:
                    hw_object = (
                        Homework.objects.filter(
                            grade=grade,
                            letter=letter,
                            subject=subject,
                        )
                        .filter(Q(group=0) | Q(group=group))
                        .order_by("-created_at")
                        .first()
                    )
                else:
                    hw_object = (
                        Homework.objects.filter(
                            grade=grade,
                            letter=letter,
                            subject=subject,
                        )
                        .filter(Q(group=0) | Q(group=group))
                        .order_by("-created_at")
                        .first()
                    )
            except Homework.DoesNotExist:
                pass
            if hw_object:
                images = [i.image.url for i in hw_object.images.all()]
                files = [i.file.url for i in hw_object.files.all()]
                serializer_data = HomeworkSerializer(hw_object).data
                serializer_data["author"] = (
                    f"{hw_object.author.first().user.first_name} "
                    f"{hw_object.author.first().user.last_name}"
                )
                serializer_data["images"] = images
                serializer_data["files"] = files
                data[subject] = serializer_data
        return HttpResponse(json.dumps(data))


class GetOneSubjectAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        user = users.models.User.objects.get(
            telegram_id=request.data["telegram_id"],
        )
        grade = user.grade
        letter = user.letter
        group = user.group
        subject = request.data["subject"]
        subject = get_abbreviation_from_name(subject)
        try:
            hw_object = (
                Homework.objects.filter(
                    grade=grade,
                    letter=letter,
                    subject=subject,
                )
                .filter(Q(group=group) | Q(group=0))
                .order_by("-created_at")
                .first()
            )
        except Homework.DoesNotExist:
            return HttpResponse("Does not exist")
        if not hw_object:
            return HttpResponse("Does not exist")
        images = [i.image.url for i in hw_object.images.all()]
        files = [i.file.url for i in hw_object.files.all()]
        serialized_data = HomeworkSerializer(hw_object).data
        serialized_data["images"] = images
        serialized_data["files"] = files
        serialized_data["author"] = (
            f"{hw_object.author.first().user.first_name} "
            f"{hw_object.author.first().user.last_name}"
        )
        return HttpResponse(json.dumps(serialized_data))


class GetAllHomeworkFromDateAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        user_obj = users.models.User.objects.get(
            telegram_id=request.data["telegram_id"],
        )
        grade = user_obj.grade
        letter = user_obj.letter
        group = user_obj.group
        year, month, day = list(map(int, request.data["date"].split(".")))
        subjects = get_user_subjects_abbreviation(grade, letter)
        data = {}
        for subject in subjects:
            try:
                hw_object = (
                    Homework.objects.filter(
                        grade=grade,
                        letter=letter,
                        subject=subject,
                    )
                    .filter(Q(group=0) | Q(group=group))
                    .filter(created_at__date=datetime(year, month, day))
                    .order_by("-created_at")
                    .first()
                )
            except Homework.DoesNotExist:
                pass
            if hw_object:
                images = [i.image.url for i in hw_object.images.all()]
                files = [i.file.url for i in hw_object.files.all()]
                serializer_data = HomeworkSerializer(hw_object).data
                serializer_data["author"] = (
                    f"{hw_object.author.first().user.first_name} "
                    f"{hw_object.author.first().user.last_name}"
                )
                serializer_data["images"] = images
                serializer_data["files"] = files
                data[subject] = serializer_data
        return HttpResponse(json.dumps(data))


class GetHomeworkFromIdAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        user_obj = users.models.User.objects.get(
            telegram_id=request.data["telegram_id"],
        )
        grade = user_obj.grade
        letter = user_obj.letter
        group = user_obj.group
        homework_id = request.data["homework_id"]
        try:
            hw_object = (
                Homework.objects.filter(
                    grade=grade,
                    letter=letter,
                    id=homework_id,
                )
                .filter(Q(group=0) | Q(group=group))
                .order_by("-created_at")
                .first()
            )
        except Homework.DoesNotExist:
            return HttpResponse("Does not exist")
        if hw_object:
            images = [i.image.url for i in hw_object.images.all()]
            files = [i.file.url for i in hw_object.files.all()]
            serializer_data = HomeworkSerializer(hw_object).data
            serializer_data["author"] = (
                f"{hw_object.author.first().user.first_name} "
                f"{hw_object.author.first().user.last_name}"
            )
            serializer_data["images"] = images
            serializer_data["files"] = files
            return HttpResponse(json.dumps(serializer_data))
        return HttpResponse("Undefined")


class GetTomorrowHomeworkAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        schedule = get_tomorrow_schedule(
            user_obj.grade,
            user_obj.letter,
            user_obj.group,
        )
        data = {}
        for lesson in schedule:
            try:
                homework_obj = (
                    Homework.objects.order_by("-created_at")
                    .filter(Q(group=0) | Q(group=user_obj.group))
                    .get(
                        grade=user_obj.grade,
                        letter=user_obj.letter,
                        subject=lesson.subject,
                    )
                )
            except Homework.DoesNotExist:
                data[lesson.lesson] = "Nothing"
            else:
                serialized_obj = HomeworkSerializer(homework_obj).data
                data[lesson.lesson] = serialized_obj
        return HttpResponse(json.dumps(data))


class AddHomeWorkAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        grade = user_obj.grade
        letter = user_obj.letter
        subject = request.data["subject"]
        description = request.data["description"]
        images = request.data["images"]
        files = request.data["files"]
        subject_abbreviation = get_abbreviation_from_name(subject)
        if subject not in ["eng1", "eng2", "ger1", "ger2", "ikt1", "ikt2"]:
            group = 0
        else:
            group = user_obj.group
        hw_object = Homework.objects.create(
            grade=grade,
            letter=letter,
            description=description,
            group=group,
            subject=subject_abbreviation,
        )
        for image in images:
            hw_object.images.add(Image.objects.create(image=image))
        for file in files:
            hw_object.images.add(Image.objects.create(file=file))
        hw_object.author.add(user_obj)
        return HttpResponse("Successful")


class EditHomeworkDescriptionAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        new_description = request.data["description"]
        grade = user_obj.grade
        letter = user_obj.letter
        group = user_obj.group
        try:
            homework_obj = Homework.objects.filter(
                Q(group=0) | Q(group=group),
            ).get(id=homework_id, grade=grade, letter=letter)
        except Homework.DoesNotExist:
            return HttpResponse("Does not exist")
        homework_obj.description = new_description
        homework_obj.save()
        return HttpResponse("Successful")


class EditHomeworkImagesAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        new_images = request.data["images"]
        grade = user_obj.grade
        letter = user_obj.letter
        group = user_obj.group
        try:
            homework_obj = Homework.objects.filter(
                Q(group=0) | Q(group=group),
            ).get(id=homework_id, grade=grade, letter=letter)
            Image.objects.filter(homework_id=homework_id).delete()
        except Homework.DoesNotExist:
            return HttpResponse("Does not exist")
        for image in new_images:
            image_object = Image.objects.create(image=image)
            homework_obj.images.add(image_object)
        return HttpResponse("Successful")


class EditHomeworkFilesAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        new_files = request.data["files"]
        grade = user_obj.grade
        letter = user_obj.letter
        group = user_obj.group
        try:
            homework_obj = Homework.objects.filter(
                Q(group=0) | Q(group=group),
            ).get(id=homework_id, grade=grade, letter=letter)
            File.objects.filter(homework_id=homework_id).delete()
        except Homework.DoesNotExist:
            return HttpResponse("Does not exist")
        for file in new_files:
            file_object = File.objects.create(file=file)
            file_name = file.split("/")[-1]
            file_object.file_name = file_name
            file_object.save()
            homework_obj.files.add(file_object)
        return HttpResponse("Successful")


class DeleteHomeworkAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        user_grade = user_obj.grade
        user_letter = user_obj.letter
        user_group = user_obj.group
        homework_id = request.data["homework_id"]
        try:
            Homework.objects.filter(Q(group=user_group) | Q(group=0)).get(
                grade=user_grade,
                letter=user_letter,
                id=homework_id,
            ).delete()
        except Homework.DoesNotExist:
            return HttpResponse("Does not exist")
        return HttpResponse("Successful")


class GetMailingAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        data = {}
        info_obj_one = (
            Homework.objects.filter(group=-1).order_by("-created_at").first()
        )
        info_obj_two = (
            Homework.objects.filter(group=-3).order_by("-created_at").first()
        )
        data["class"] = HomeworkSerializer(info_obj_one).data
        data["school"] = HomeworkSerializer(info_obj_two).data
        if django_user.is_staff or django_user.is_superuser:
            info_obj_three = (
                Homework.objects.filter(group=-2)
                .order_by("-created_at")
                .first()
            )
            data["admins"] = HomeworkSerializer(info_obj_three).data
        return HttpResponse(json.dumps(data))


class AddMailingAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        level = request.data["level"]
        if level == "class":
            if not django_user.is_staff or not django_user.is_superuser:
                return HttpResponse("Not allowed")
            grade = user_obj.grade
            letter = user_obj.letter
            images = request.data["images"]
            files = request.data["files"]
            homework_obj = Homework.objects.create(grade=grade, letter=letter)
            for image in images:
                image_obj = Image.objects.create(image=image)
                homework_obj.images.add(image_obj)
            for file in files:
                file_obj = File.objects.create(file=file)
                homework_obj.files.add(file_obj)
            homework_obj.group = -1
            homework_obj.description = request.data["description"]
            homework_obj.subject = "info"
            homework_obj.save()
            return HttpResponse("Successful")
        if not django_user.is_superuser:
            return HttpResponse("Not allowed")
        grade = user_obj.grade
        letter = user_obj.letter
        images = request.data["images"]
        files = request.data["files"]
        homework_obj = Homework.objects.create(grade=grade, letter=letter)
        for image in images:
            image_obj = Image.objects.create(image=image)
            homework_obj.images.add(image_obj)
        for file in files:
            file_obj = File.objects.create(file=file)
            homework_obj.files.add(file_obj)
        if level == "admins":
            homework_obj.group = -2
        elif level == "school":
            homework_obj.group = -3
        homework_obj.description = request.data["description"]
        homework_obj.subject = "info"
        homework_obj.author.add(user_obj)
        homework_obj.save()
        return HttpResponse("Successful")


class EditMailingAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        homework_id = request.data["homework_id"]
        if django_user.is_superuser:
            try:
                homework_obj = Homework.objects.filter(
                    Q(group=-1) | Q(group=-2) | Q(group=-3),
                ).get(id=homework_id)
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist")
        elif django_user.is_staff:
            try:
                homework_obj = (
                    Homework.objects.filter(group=-1).get(id=homework_id),
                )
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist | Not allowed")
        serialized_data = HomeworkSerializer(homework_obj).data
        images = [i.image.url for i in homework_obj.images.all()]
        files = [i.file.url for i in homework_obj.files.all()]
        serialized_data["images"] = images
        serialized_data["files"] = files
        if homework_obj.group != -3:
            serialized_data["author"] = (
                f"{homework_obj.author.first().user.first_name} "
                f"{homework_obj.author.first().user.last_name}"
            )
        return HttpResponse(json.dumps(serialized_data))


class EditMailingDescriptionAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        new_description = request.data["description"]
        homework_obj = None
        if django_user.is_superuser:
            try:
                homework_obj = Homework.objects.get(id=homework_id)
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist")
        elif django_user.is_staff:
            try:
                homework_obj = (
                    Homework.objects.filter(group=-1).get(id=homework_id),
                )
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist | Not allowed")
        if not homework_obj:
            return HttpResponse("Error")
        homework_obj.description = new_description
        homework_obj.save()
        return HttpResponse("Successful")


class EditMailingImagesAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        new_images = request.data["images"]
        if django_user.is_superuser:
            try:
                homework_obj = Homework.objects.get(id=homework_id)
                Image.objects.filter(homework_id=homework_id).delete()
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist")
        elif django_user.is_staff:
            try:
                homework_obj = Homework.objects.get(id=homework_id, group=-1)
                Image.objects.filter(homework_id=homework_id).delete()
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist | Not allowed")
        for image in new_images:
            image_object = Image.objects.create(image=image)
            homework_obj.images.add(image_object)
        return HttpResponse("Successful")


class EditMailingFilesAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        new_files = request.data["files"]
        if django_user.is_superuser:
            try:
                homework_obj = Homework.objects.get(id=homework_id)
                File.objects.filter(homework_id=homework_id).delete()
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist")
        elif django_user.is_staff:
            try:
                homework_obj = Homework.objects.get(id=homework_id, group=-1)
                File.objects.filter(homework_id=homework_id).delete()
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist | Not allowed")
        for file in new_files:
            file_object = File.objects.create(file=file)
            file_name = file.split("/")[-1]
            file_object.file_name = file_name
            file_object.save()
            homework_obj.files.add(file_object)
        return HttpResponse("Successful")


class DeleteMailingAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        if django_user.is_superuser:
            try:
                Homework.objects.get(
                    id=homework_id,
                ).delete()
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist")
        elif django_user.is_staff:
            try:
                Homework.objects.get(
                    group=-1,
                    id=homework_id,
                ).delete()
            except Homework.DoesNotExist:
                return HttpResponse("Does not exist | Not allowed")
        return HttpResponse("Successful")


class TodoWorkAPI(APIView):
    @staticmethod
    def post(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        homework_id = request.data["homework_id"]
        homework_obj = Homework.objects.get(id=homework_id)
        try:
            homework_todo = Todo.objects.get(
                user_todo=user_obj,
                homework_todo=homework_obj,
            )
        except Todo.DoesNotExist:
            todo_obj = Todo.objects.create()
            todo_obj.user_todo.add(user_obj)
            todo_obj.homework_todo.add(homework_obj)
            todo_obj.is_done = True
            todo_obj.save()
        else:
            homework_todo.is_done = not homework_todo.is_done
            homework_todo.save()
        return HttpResponse("Successful")


class GetTomorrowScheduleAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        schedule = get_tomorrow_schedule(
            user_obj.grade,
            user_obj.letter,
            user_obj.group,
        )
        date = {}
        for lesson in schedule:
            date[lesson.lesson] = lesson.subject
        return HttpResponse(json.dumps(date))


class DeleteOldHomeworkAPI(APIView):
    @staticmethod
    def get(request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        if not user_obj.user.is_superuser:
            return HttpResponse("Not allowed ^)")

        today = datetime.today().date()
        two_weeks_ago = today - timedelta(days=14)
        todo_objects = Todo.objects.filter(created_at__lt=two_weeks_ago)
        hw_objects = Homework.objects.filter(created_at__lt=two_weeks_ago)
        response_message = (
            f"Successful delete {todo_objects.count()}"
            f" Todo and {hw_objects.count()}"
            f" Homework rows",
        )
        todo_objects.delete()
        hw_objects.delete()
        return HttpResponse(response_message)
