import json

from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.views import View

from homework.forms import ChooseGradLetForm
from homework.models import File, Homework, Image


class HomeworkPage(View):
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
        data = Homework.objects.filter(grade=grade, letter=letter).all()
        return render(
            request,
            "homework/homework.html",
            context={
                "homework": data,
            },
        )


class ChooseGrLePage(View):
    def get(self, request):
        grade = request.COOKIES.get("grade")
        letter = request.COOKIES.get("letter")
        return render(
            request,
            "homework/choose_grad_let.html",
            context={
                "grade": grade,
                "letter": letter,
                "form": ChooseGradLetForm,
            },
        )

    def post(self, request):
        data = {
            "grade": request.POST.get("grade"),
            "letter": request.POST.get("letter"),
        }
        response = redirect("homework:homework_page")
        response.set_cookie("hw_data", json.dumps(data))
        return response


class AddHomeworkPage(View):
    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            return render(
                request,
                "homework/addhomework.html",
            )
        return redirect("homework:homework_page")

    def post(self, request):
        if not request.user.is_staff or request.user.is_superuser:
            return redirect("homework:homework_page")
        description = request.POST["description"]
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
        homework_object = Homework.objects.create(
            description=description,
            grade=server_user.grade,
            letter=server_user.letter,
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
            hw_info = Homework.objects.get(id=homework_id)
            return render(
                request,
                "homework/delete_homework.html",
                context={"hw_info": hw_info},
            )
        return redirect("homework:homework_page")

    def post(self, request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            Homework.objects.get(
                id=homework_id,
                grade=request_user.grade,
                letter=request_user.letter,
            ).delete()
        return redirect("homework:homework_page")


class EditHomework(View):
    def get(self, request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            hw_info = Homework.objects.get(
                id=homework_id,
                grade=request_user.grade,
                letter=request_user.letter,
            )
            return render(
                request,
                "homework/edit_homework.html",
                context={"hw_info": hw_info},
            )
        return redirect("homework:homework_page")

    def post(self, request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            description = request.POST["description"]
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
            homework_object = Homework.objects.get(
                id=homework_id,
                grade=server_user.grade,
                letter=server_user.letter,
            )

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
            homework_object.save()
            return redirect("homework:edit_homework", homework_id=homework_id)
        return redirect("homework:homework_page")


class EditHomeworkData(View):
    def get(self, request, homework_id, r_type, file_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            hw_object = Homework.objects.get(
                id=homework_id,
                grade=request_user.grade,
                letter=request_user.letter,
            )
            if r_type == "img":
                Image.objects.get(id=file_id, homework=hw_object).delete()
            elif r_type == "file":
                File.objects.get(id=file_id, homework=hw_object).delete()
            return redirect("homework:edit_homework", homework_id=homework_id)
        return redirect("homework:homework_page")
