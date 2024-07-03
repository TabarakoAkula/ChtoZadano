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
        data = []
        for subject in subjects:
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
            if hw_object:
                data.append(hw_object)
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
        else:
            try:
                data = json.loads(request.COOKIES.get("hw_data"))
            except TypeError:
                return redirect("homework:choose_grad_let")
            grade = data["grade"]
            letter = data["letter"]
            if not grade or not letter:
                return redirect("homework:choose_grad_let")
        data = (
            Homework.objects.filter(
                grade=grade,
                letter=letter,
            )
            .filter(Q(group=0) | Q(group=request.user.server_user.group))
            .order_by("-subject", "-created_at")
            .all()
        )
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
            group = request.POST["group"]
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
            homework_object.group = group
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
        subjects = get_user_subjects_abbreviation(grade, letter)
        data = {}
        for subject in subjects:
            hw_object = (
                Homework.objects.filter(
                    grade=grade,
                    letter=letter,
                    subject=subject,
                )
                .order_by("-created_at")
                .first()
            )
            if hw_object:
                serializer_data = HomeworkSerializer(hw_object).data
                serializer_data["author"] = (
                    f"{hw_object.author.first().user.first_name} "
                    f"{hw_object.author.first().user.last_name}"
                )
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
        return HttpResponse(json.dumps(HomeworkSerializer(hw_object).data))
