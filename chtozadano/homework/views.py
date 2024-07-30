import json

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import generic, View

from homework.forms import ChooseGradLetForm
from homework.models import File, Homework, Image, Todo
from homework.utils import (
    check_grade_letter,
    get_abbreviation_from_name,
    get_all_schedule,
    get_name_from_abbreviation,
    get_user_subjects,
    get_user_subjects_abbreviation,
    save_files,
)
import users.models


class HomeworkPage(View):
    @staticmethod
    def get(request):
        checker = check_grade_letter(request)
        if checker[0] == "Error":
            return checker[1]
        grade, letter, group = checker[1]
        subjects = get_user_subjects_abbreviation(grade, letter)
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
                        .order_by("group", "-created_at")
                        .first()
                    )
                if hw_object:
                    data.append(hw_object)
            except Homework.DoesNotExist:
                pass
        for homework in data:
            homework.subject = get_name_from_abbreviation(homework.subject)
        if request.user.is_authenticated:
            done_list = Todo.objects.filter(
                user_todo=request.user.server_user,
                is_done=True,
            ).all()
            done_list = [i.homework_todo.first().id for i in done_list]
        else:
            done_list = []
        info = []
        school_obj = (
            Homework.objects.filter(
                subject="info",
                group=-3,
            )
            .order_by("-created_at")
            .first(),
        )
        if school_obj:
            info.append(school_obj)
        if request.user.is_staff or request.user.is_superuser:
            admin_obj = (
                Homework.objects.filter(
                    subject="info",
                    group=-2,
                )
                .order_by("-created_at")
                .first(),
            )
            if admin_obj:
                info.append(admin_obj)
        class_obj = (
            Homework.objects.filter(
                subject="info",
                group=-1,
            )
            .order_by("-created_at")
            .first(),
        )
        if class_obj:
            info.append(class_obj)
        info = [i[0] for i in info]
        return render(
            request,
            "homework/homework.html",
            context={
                "homework": data,
                "info": info,
                "done_list": done_list,
            },
        )


class AllHomeworkPage(generic.ListView):
    model = Homework
    template_name = "homework/all_homework.html"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        checker = check_grade_letter(request)
        if checker[0] == "Error":
            return checker[1]
        self.grade, self.letter, self.group = checker[1]
        self.is_authenticated = request.user.is_authenticated
        self.is_staff = request.user.is_staff
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        data = ()
        try:
            if self.is_authenticated and self.is_staff:
                data = (
                    Homework.objects.filter(
                        grade=self.grade,
                        letter=self.letter,
                    )
                    .filter(Q(group=0) | Q(group=self.group))
                    .order_by("-created_at")
                    .all()
                )
            else:
                data = (
                    Homework.objects.filter(
                        grade=self.grade,
                        letter=self.letter,
                    )
                    .filter(Q(group=0) | Q(group=self.group))
                    .order_by("group", "-subject", "-created_at")
                    .all()
                )
        except Homework.DoesNotExist:
            pass
        for homework in data:
            homework.subject = get_name_from_abbreviation(homework.subject)
        return data


class ChooseGrLePage(View):
    @staticmethod
    def get(request):
        if request.user.is_staff and not request.user.is_superuser:
            return redirect("homework:homework_page")
        return render(
            request,
            "homework/choose_grad_let.html",
            context={
                "form": ChooseGradLetForm,
            },
        )

    @staticmethod
    def post(request):
        if request.user.is_staff and not request.user.is_superuser:
            return redirect("homework:homework_page")
        grade = request.POST.get("grade")
        letter = request.POST.get("letter")
        group = request.POST.get("group")
        data = {
            "grade": grade,
            "letter": letter,
            "group": group,
        }
        response = redirect("homework:homework_page")
        response.set_cookie("hw_data", json.dumps(data))
        if request.user.is_authenticated:
            user_obj = users.models.User.objects.get(user=request.user)
            user_obj.grade = grade
            user_obj.letter = letter
            user_obj.group = group
            user_obj.save()
        messages.success(
            request,
            f"Класс и литера успешно изменены, сейчас"
            f" вы в {grade}{letter} классе, группа {group}",
        )
        return response


class AddHomeworkPage(View):
    @staticmethod
    def get(request):
        if request.user.is_staff or request.user.is_superuser:
            user = request.user.server_user
            grade, letter, group = user.grade, user.letter, user.group
            response_list = get_user_subjects(grade, letter, group)
            return render(
                request,
                "homework/add_homework.html",
                context={"subjects": response_list},
            )
        messages.error(
            request,
            "Для добавления домашнего задания у вас"
            " должны быть права администратора",
        )
        return redirect("homework:homework_page")

    @staticmethod
    def post(request):
        if not request.user.is_staff or not request.user.is_superuser:
            messages.error(
                request,
                "Для добавления домашнего задания у вас"
                " должны быть права администратора",
            )
            return redirect("homework:homework_page")
        description = request.POST["description"]
        subject = request.POST["subject"]
        subject = get_abbreviation_from_name(subject)
        request_files_list = request.FILES.getlist("files")
        files_list_for_model = save_files(request_files_list)
        files_list_for_model = files_list_for_model[1]
        server_user = request.user.server_user
        if subject not in [
            "eng1",
            "eng2",
            "ger1",
            "ger2",
            "ikt1",
            "ikt2",
        ]:
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
        messages.success(request, "Домашнее задание успешно добавлено")
        return redirect("homework:homework_page")


class EditHomework(View):
    @staticmethod
    def get(request, homework_id):
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
                messages.error(request, "Такой записи не существует")
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
        messages.error(
            request,
            "Для редактирования домашнего задания у вас"
            " должны быть права администратора",
        )
        return redirect("homework:homework_page")

    @staticmethod
    def post(request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            description = request.POST["description"]
            subject = request.POST["subject"]
            subject = get_abbreviation_from_name(subject)
            request_files_list = request.FILES.getlist("files")
            files_list_for_model = save_files(request_files_list)
            if files_list_for_model[0] == "Error":
                messages.error(request, "Неподходящий формат файла")
                return render(
                    request,
                    "homework/add_homework.html",
                    context={
                        "errors": ("Unsupported file format",),
                    },
                )
            files_list_for_model = files_list_for_model[1]
            server_user = request.user.server_user
            try:
                homework_object = Homework.objects.get(
                    id=homework_id,
                    grade=server_user.grade,
                    letter=server_user.letter,
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
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
            messages.success(request, "Успешно обновлено")
            return redirect("homework:edit_homework", homework_id=homework_id)
        messages.error(
            request,
            "Для редактирования домашнего задания у вас"
            " должны быть права администратора",
        )
        return redirect("homework:homework_page")


class EditHomeworkData(View):
    @staticmethod
    def get(request, homework_id, r_type, file_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            try:
                hw_object = Homework.objects.get(
                    id=homework_id,
                    grade=request_user.grade,
                    letter=request_user.letter,
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            if r_type == "img":
                Image.objects.get(id=file_id, homework=hw_object).delete()
            elif r_type == "file":
                File.objects.get(id=file_id, homework=hw_object).delete()
            messages.success(request, "Успешно обновлено")
            return redirect("homework:edit_homework", homework_id=homework_id)
        messages.error(
            request,
            "Для редактирования домашнего задания у вас"
            " должны быть права администратора",
        )
        return redirect("homework:homework_page")


class DeleteHomework(View):
    @staticmethod
    def get(request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            try:
                hw_info = Homework.objects.get(
                    id=homework_id,
                    grade=request_user.grade,
                    letter=request_user.letter,
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            return render(
                request,
                "homework/delete_homework.html",
                context={"hw_info": hw_info},
            )
        messages.error(
            request,
            "Для удаления домашнего задания у вас"
            " должны быть права администратора",
        )
        return redirect("homework:homework_page")

    @staticmethod
    def post(request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            try:
                Homework.objects.get(
                    id=homework_id,
                    grade=request_user.grade,
                    letter=request_user.letter,
                ).delete()
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            messages.success(request, "Домашнее задание успешно удалено")
        return redirect("homework:homework_page")


class AddMailingPage(View):
    @staticmethod
    def get(request):
        if request.user.is_superuser:
            response_list = [
                "Сообщение для класса",
                "Сообщение для администраторов",
                "Сообщение для всей школы",
            ]
        elif request.user.is_staff:
            response_list = [
                "Сообщение для класса",
            ]
        else:
            messages.error(
                request,
                "Для добавления рассылки у вас"
                " должны быть права администратора",
            )
            return redirect("homework:homework_page")
        return render(
            request,
            "homework/add_homework.html",
            context={"subjects": response_list},
        )

    @staticmethod
    def post(request):
        if not request.user.is_superuser or not request.user.is_staff:
            messages.error(
                request,
                "Для добавления рассылки у вас"
                " должны быть права администратора",
            )
            return redirect("homework:homework_page")
        description = request.POST["description"]
        request_subject = request.POST["subject"]
        if request_subject == "Сообщение для класса":
            group = -1
        elif request_subject == "Сообщение для администраторов":
            group = -2
        else:
            group = -3
        request_files_list = request.FILES.getlist("files")
        files_list_for_model = save_files(request_files_list)
        if files_list_for_model[0] == "Error":
            render(
                request,
                "homework/add_homework.html",
                context={
                    "errors": "Unsupported file format",
                },
            )
        files_list_for_model = files_list_for_model[1]
        server_user = request.user.server_user
        homework_object = Homework.objects.create(
            description=description,
            grade=0,
            letter="",
            subject="info",
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
        messages.success(request, "Рассылка успешно добавлена")
        return redirect("homework:homework_page")


class EditMailingPage(View):
    @staticmethod
    def get(request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            user_subjects = []
            if request.user.is_superuser:
                user_subjects.append("Сообщение для администраторов")
                user_subjects.append("Сообщение для всей школы")
            if request.user.is_staff:
                user_subjects.append("Сообщение для класса")
            try:
                hw_info = Homework.objects.order_by("-created_at").get(
                    id=homework_id,
                    subject="info",
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            if hw_info.group == -1:
                subject_now = "Сообщение для класса"
            elif hw_info.group == -2:
                subject_now = "Сообщение для администраторов"
            elif hw_info.group == -3:
                subject_now = "Сообщение для всей школы"
            return render(
                request,
                "homework/edit_homework.html",
                context={
                    "hw_info": hw_info,
                    "subjects": user_subjects,
                    "subject_now": subject_now,
                },
            )
        messages.error(
            request,
            "Для редактирования рассылки у вас"
            " должны быть права администратора",
        )
        return redirect("homework:homework_page")

    @staticmethod
    def post(request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            description = request.POST["description"]
            request_subject = request.POST["subject"]
            if request_subject == "Сообщение для класса":
                group = -1
            elif request_subject == "Сообщение для администраторов":
                group = -2
            else:
                group = -3
            request_files_list = request.FILES.getlist("files")
            files_list_for_model = save_files(request_files_list)
            if files_list_for_model[0] == "Error":
                messages.error(request, "Неподходящий формат файла")
                return render(
                    request,
                    "homework/add_homework.html",
                    context={
                        "errors": ("Unsupported file format"),
                    },
                )
            files_list_for_model = files_list_for_model[1]
            try:
                homework_object = Homework.objects.get(
                    id=homework_id,
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
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
            homework_object.group = group
            homework_object.save()
            messages.success(request, "Успешно обновлено")
            return redirect("homework:edit_mailing", homework_id=homework_id)
        messages.error(
            request,
            "Для редактирования рассылки у вас"
            " должны быть права администратора",
        )
        return redirect("homework:homework_page")


class DeleteMailing(View):
    @staticmethod
    def get(request, homework_id):
        if request.user.is_superuser:
            try:
                hw_info = Homework.objects.get(
                    id=homework_id,
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            return render(
                request,
                "homework/delete_homework.html",
                context={"hw_info": hw_info},
            )
        if request.user.is_staff:
            try:
                hw_info = Homework.objects.get(
                    id=homework_id,
                    group=-1,
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            return render(
                request,
                "homework/delete_homework.html",
                context={"hw_info": hw_info},
            )
        messages.error(
            request,
            f"Для удаления рассылки у вас"
            f" должны быть права администратора{''}",
        )
        return redirect("homework:homework_page")

    @staticmethod
    def post(request, homework_id):
        if request.user.is_superuser:
            try:
                Homework.objects.get(
                    id=homework_id,
                ).delete()
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            messages.success(request, "Рассылка успешно удалена")
        elif request.user.is_staff:
            try:
                Homework.objects.get(
                    id=homework_id,
                    group=-1,
                ).delete()
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            messages.success(request, "Рассылка успешно удалена")
        else:
            messages.error(
                request,
                "Для удаления рассылки у вас"
                " должны быть права администратора",
            )
        return redirect("homework:homework_page")


class MarkDone(View):
    @staticmethod
    def get(request, homework_id):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "Необходимо войти в аккаунт для этого действия",
            )
            return redirect("users:signin_page")
        try:
            user = users.models.User.objects.get(user=request.user)
            homework = Homework.objects.get(id=homework_id)
            todo_obj = Todo.objects.filter(
                user_todo=user,
                homework_todo=homework,
            ).first()
            if todo_obj:
                if todo_obj.is_done:
                    todo_obj.is_done = False
                else:
                    todo_obj.is_done = True
                todo_obj.save()
            else:
                todo_obj = Todo.objects.create()
                todo_obj.user_todo.add(user)
                todo_obj.homework_todo.add(homework)
                todo_obj.is_done = True
                todo_obj.save()
        except users.models.User.DoesNotExist and Homework.DoesNotExist:
            return redirect("homework:homework_page")
        return redirect("homework:homework_page")


class SchedulePage(View):
    @staticmethod
    def get(request):
        checker = check_grade_letter(request)
        if checker[0] == "Error":
            return checker[1]
        schedule = get_all_schedule(*checker[1])
        for day in schedule:
            for lesson in day:
                lesson.subject = get_name_from_abbreviation(lesson.subject)
        return render(
            request,
            "homework/schedule.html",
            context={"data": schedule},
        )
