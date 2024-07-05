from datetime import datetime
import json

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.views import APIView

from homework.forms import ChooseGradLetForm
from homework.models import File, Homework, Image
from homework.serializers import HomeworkSerializer
from homework.utils import (
    get_abbreviation_from_name,
    get_name_from_abbreviation,
    get_user_subjects,
    get_user_subjects_abbreviation,
)
import users.forms
import users.models


class HomeworkPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            grade = request.user.server_user.grade
            letter = request.user.server_user.letter
            group = request.user.server_user.group
        else:
            try:
                data = json.loads(request.COOKIES.get("hw_data"))
            except TypeError:
                return redirect("homework:choose_grad_let")
            grade = data["grade"]
            letter = data["letter"]
            group = data["group"]
            if not grade or not letter:
                return redirect("homework:choose_grad_let")
        subjects = get_user_subjects_abbreviation(grade, letter)
        subjects.insert(0, "info")
        data = []
        for subject in subjects:
            try:
                if request.user.is_staff:
                    hw_object = (
                        Homework.objects.filter(
                            grade=grade,
                            letter=letter,
                            subject=subject,
                        )
                        .filter(
                            Q(group=0)
                            | Q(group=group)
                            | Q(group=-1)
                            | Q(group=-2)
                            | Q(group=-3),
                        )
                        .order_by("group", "-created_at")
                        .first()
                    )
                else:
                    hw_object = (
                        Homework.objects.filter(
                            grade=grade,
                            letter=letter,
                            subject=subject,
                        )
                        .filter(
                            Q(group=0)
                            | Q(group=group)
                            | Q(group=-1)
                            | Q(group=-3),
                        )
                        .order_by("group", "-created_at")
                        .first()
                    )
                if hw_object:
                    data.append(hw_object)
            except Homework.DoesNotExist:
                pass
        return render(
            request,
            "homework/homework.html",
            context={
                "homework": data,
            },
        )


class AllHomeworkPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            grade = request.user.server_user.grade
            letter = request.user.server_user.letter
            group = request.user.server_user.group
        else:
            try:
                data = json.loads(request.COOKIES.get("hw_data"))
            except TypeError:
                return redirect("homework:choose_grad_let")
            grade = data["grade"]
            letter = data["letter"]
            group = data["group"]
            if not grade or not letter:
                return redirect("homework:choose_grad_let")
        try:
            if request.user.is_authenticated and request.user.is_staff:
                data = (
                    Homework.objects.filter(
                        grade=grade,
                        letter=letter,
                    )
                    .filter(
                        Q(group=0)
                        | Q(group=group)
                        | Q(group=-1)
                        | Q(group=-2)
                        | Q(group=-3),
                    )
                    .order_by("group", "-subject", "-created_at")
                    .all()
                )
            else:
                data = (
                    Homework.objects.filter(
                        grade=grade,
                        letter=letter,
                    )
                    .filter(
                        Q(group=0)
                        | Q(group=group)
                        | Q(group=-1)
                        | Q(group=-3),
                    )
                    .order_by("group", "-subject", "-created_at")
                    .all()
                )
        except Homework.DoesNotExist:
            pass
        return render(
            request,
            "homework/all_homework.html",
            context={
                "homework": data,
            },
        )


class ChooseGrLePage(View):
    def get(self, request):
        if request.user.is_staff:
            return redirect("homework:homework_page")
        return render(
            request,
            "homework/choose_grad_let.html",
            context={
                "form": ChooseGradLetForm,
            },
        )

    def post(self, request):
        if request.user.is_staff:
            return redirect("homework:homework_page")
        data = {
            "grade": request.POST.get("grade"),
            "letter": request.POST.get("letter"),
            "group": request.POST.get("group"),
        }
        response = redirect("homework:homework_page")
        response.set_cookie("hw_data", json.dumps(data))
        return response


class AddHomeworkPage(View):
    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            user = request.user.server_user
            grade, letter, group = user.grade, user.letter, user.group
            response_list = get_user_subjects(grade, letter, group)
            return render(
                request,
                "homework/addhomework.html",
                context={"subjects": response_list, "groups": [0, group]},
            )
        return redirect("homework:homework_page")

    def post(self, request):
        if not request.user.is_staff or request.user.is_superuser:
            return redirect("homework:homework_page")
        description = request.POST["description"]
        subject = request.POST["subject"]
        subject = get_abbreviation_from_name(subject)
        request_files_list = request.FILES.getlist("files")
        files_list_for_model = []
        for r_file in request_files_list:
            file_extension = r_file.name.split(".")[-1]
            if file_extension.lower() in ["png", "jpeg", "webp", "gif", "jpg"]:
                file_name = default_storage.save(
                    f"homework/img/{r_file.name}",
                    r_file,
                )
                files_list_for_model.append((file_name, "img"))
            elif file_extension.lower() in [
                "pdf",
                "ppt",
                "pptx",
                "doc",
                "docx",
                "zip",
            ]:
                file_name = default_storage.save(
                    f"homework/files/{r_file.name}",
                    r_file,
                )
                files_list_for_model.append((file_name, "file"))
            elif file_extension.lower() in ["mp3", "ogg", "acc", "wav"]:
                file_name = default_storage.save(
                    f"homework/music/{r_file.name}",
                    r_file,
                )
                files_list_for_model.append((file_name, "music"))
            else:
                return render(
                    request,
                    "homework/addhomework.html",
                    context={
                        "errors": (
                            f"Unsupported file format: {file_extension}",
                        ),
                    },
                )
        server_user = request.user.server_user
        if subject not in ["eng1", "eng2", "ger1", "ger2", "ikt1", "ikt2"]:
            group = 0
        else:
            group = server_user.group
        homework_object = Homework.objects.create(
            description=description,
            grade=server_user.grade,
            letter=server_user.letter,
            subject=subject,
            group=group,
        )
        homework_object.author.add(server_user)

        for file in files_list_for_model:
            file_name = file[0]
            file_type = file[1]
            if file_type == "img":
                image_object = Image.objects.create(
                    image=file_name,
                    homework=homework_object,
                )
                homework_object.images.add(image_object)
            else:
                file_object = File.objects.create(
                    file=file_name,
                    homework=homework_object,
                    file_name=file_name.split("/")[-1],
                )
                homework_object.files.add(file_object)
        return redirect("homework:homework_page")


class DeleteHomework(View):
    def get(self, request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            try:
                hw_info = Homework.objects.get(
                    id=homework_id,
                    grade=request_user.grade,
                    letter=request_user.letter,
                )
            except Homework.DoesNotExist:
                return redirect("homework:homework_page")
            return render(
                request,
                "homework/delete_homework.html",
                context={"hw_info": hw_info},
            )
        return redirect("homework:homework_page")

    def post(self, request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            try:
                Homework.objects.get(
                    id=homework_id,
                    grade=request_user.grade,
                    letter=request_user.letter,
                ).delete()
            except Homework.DoesNotExist:
                return redirect("homework:homework_page")
        return redirect("homework:homework_page")


class EditHomework(View):
    def get(self, request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            user_subjects = get_user_subjects(
                request_user.grade,
                request_user.letter,
                request_user.group,
            )
            group = request.user.server_user.group
            try:
                hw_info = (
                    Homework.objects.filter(Q(group=0) | Q(group=group)).get(
                        id=homework_id,
                        grade=request_user.grade,
                        letter=request_user.letter,
                    ),
                )[0]
            except Homework.DoesNotExist:
                return redirect("homework:homework_page")
            return render(
                request,
                "homework/edit_homework.html",
                context={
                    "hw_info": hw_info,
                    "subjects": user_subjects,
                    "groups": [0, group],
                    "subject_now": get_name_from_abbreviation(hw_info.subject),
                },
            )
        return redirect("homework:homework_page")

    def post(self, request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            description = request.POST["description"]
            subject = request.POST["subject"]
            subject = get_abbreviation_from_name(subject)
            request_files_list = request.FILES.getlist("files")
            files_list_for_model = []
            for r_file in request_files_list:
                file_extension = r_file.name.split(".")[-1]
                if file_extension.lower() in [
                    "png",
                    "jpeg",
                    "webp",
                    "gif",
                    "jpg",
                ]:
                    file_name = default_storage.save(
                        f"homework/img/{r_file.name}",
                        r_file,
                    )
                    files_list_for_model.append((file_name, "img"))
                elif file_extension.lower() in [
                    "pdf",
                    "ppt",
                    "pptx",
                    "doc",
                    "docx",
                    "zip",
                ]:
                    file_name = default_storage.save(
                        f"homework/files/{r_file.name}",
                        r_file,
                    )
                    files_list_for_model.append((file_name, "file"))
                elif file_extension.lower() in ["mp3", "ogg", "acc", "wav"]:
                    file_name = default_storage.save(
                        f"homework/music/{r_file.name}",
                        r_file,
                    )
                    files_list_for_model.append((file_name, "music"))
                else:
                    return render(
                        request,
                        "homework/addhomework.html",
                        context={
                            "errors": (
                                f"Unsupported file format: {file_extension}",
                            ),
                        },
                    )
            server_user = request.user.server_user
            try:
                homework_object = Homework.objects.get(
                    id=homework_id,
                    grade=server_user.grade,
                    letter=server_user.letter,
                )
            except Homework.DoesNotExist:
                return redirect("homework:homework_page")

            for file in files_list_for_model:
                file_name = file[0]
                file_type = file[1]
                if file_type == "img":
                    image_object = Image.objects.create(
                        image=file_name,
                        homework=homework_object,
                    )
                    homework_object.images.add(image_object)
                else:
                    file_object = File.objects.create(
                        file=file_name,
                        homework=homework_object,
                        file_name=file_name.split("/")[-1],
                    )
                    homework_object.files.add(file_object)

            homework_object.description = description
            homework_object.subject = subject
            homework_object.save()
            return redirect("homework:edit_homework", homework_id=homework_id)
        return redirect("homework:homework_page")


class EditHomeworkData(View):
    def get(self, request, homework_id, r_type, file_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            try:
                hw_object = Homework.objects.get(
                    id=homework_id,
                    grade=request_user.grade,
                    letter=request_user.letter,
                )
            except Homework.DoesNotExist:
                return redirect("homework:homework_page")
            if r_type == "img":
                Image.objects.get(id=file_id, homework=hw_object).delete()
            elif r_type == "file":
                File.objects.get(id=file_id, homework=hw_object).delete()
            return redirect("homework:edit_homework", homework_id=homework_id)
        return redirect("homework:homework_page")


class GetLastHomeworkAPI(APIView):
    def get(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        user = users.models.User.objects.get(
            telegram_id=request.data["telegram_id"],
        )
        grade = user.grade
        letter = user.letter
        group = user.group
        subjects = get_user_subjects_abbreviation(grade, letter)
        subjects.insert(0, "info")
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
                        .filter(
                            Q(group=0)
                            | Q(group=group)
                            | Q(group=-1)
                            | Q(group=-2)
                            | Q(group=-3),
                        )
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
                        .filter(
                            Q(group=0)
                            | Q(group=group)
                            | Q(group=-1)
                            | Q(group=-3),
                        )
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
    def get(self, request):
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
        images = [i.image.url for i in hw_object.images.all()]
        files = [i.file.url for i in hw_object.files.all()]
        serialized_data = HomeworkSerializer(hw_object).data
        serialized_data["images"] = images
        serialized_data["files"] = files
        serialized_data["author"] = user.user.first_name
        return HttpResponse(json.dumps(serialized_data))


class GetAllHomeworkFromDateAPI(APIView):
    def get(self, request):
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
    def get(self, request):
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


class DeleteHomeworkAPI(APIView):
    def post(self, request):
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


class AddHomeWorkAPI(APIView):
    def post(self, request):
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


class EditHomeworkAPI(APIView):
    def get(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        user_obj = users.models.User.objects.get(telegram_id=telegram_id)
        django_user = user_obj.user
        if not django_user.is_staff or not django_user.is_superuser:
            return HttpResponse("Not allowed")
        homework_id = request.data["homework_id"]
        user_grade = user_obj.grade
        user_letter = user_obj.letter
        user_group = user_obj.group
        try:
            homework_obj = Homework.objects.filter(
                Q(group=0) | Q(group=user_group),
            ).get(grade=user_grade, letter=user_letter, id=homework_id)
        except Homework.DoesNotExist:
            return HttpResponse("Does not exist")
        serialized_data = HomeworkSerializer(homework_obj).data
        images = [i.image.url for i in homework_obj.images.all()]
        files = [i.file.url for i in homework_obj.files.all()]
        serialized_data["images"] = images
        serialized_data["files"] = files
        serialized_data["author"] = django_user.first_name
        return HttpResponse(json.dumps(serialized_data))


class EditHomeworkDescriptionAPI(APIView):
    def post(self, request):
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
    def post(self, request):
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
    def post(self, request):
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


class AddMailingAPI(APIView):
    def post(self, request):
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


class GetMailingAPI(APIView):
    def get(self, request):
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
