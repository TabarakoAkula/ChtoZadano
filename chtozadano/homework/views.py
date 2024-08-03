import json

from django.contrib import messages
from django.db.models import OuterRef, Q, Subquery
from django.shortcuts import redirect, render, reverse
from django.views import generic, View

from homework.forms import ChooseGradLetForm
from homework.models import File, Homework, Image, Schedule, Todo
from homework.utils import (
    check_grade_letter,
    get_abbreviation_from_name,
    get_list_of_dates,
    get_name_from_abbreviation,
    get_schedule_from_weekday,
    get_user_subjects,
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
        latest_homework_ids = (
            Homework.objects.filter(Q(group=0) | Q(group=group))
            .filter(
                grade=grade,
                letter=letter,
                subject=OuterRef("subject"),
                created_at=Subquery(
                    Homework.objects.filter(
                        subject=OuterRef("subject"),
                    )
                    .values("created_at")
                    .order_by("-created_at")[:1],
                ),
            )
            .values("id")
        )
        data = (
            Homework.objects.filter(id__in=latest_homework_ids)
            .order_by("subject")
            .prefetch_related("images", "files")
            .defer("grade", "letter", "group")
        )
        data_subjects = []
        for homework_obj in data:
            abbreviation = get_name_from_abbreviation(homework_obj.subject)
            homework_obj.subject = abbreviation
            data_subjects.append(abbreviation)
        real_subjects = get_user_subjects(grade, letter, group)
        if isinstance(real_subjects, dict):
            messages.error(
                request,
                f"В {real_subjects['grade']} классе нет"
                f" литеры {real_subjects['letter']}",
            )
            return redirect("homework:choose_grad_let")
        null_subjects = list(set(real_subjects) - set(data_subjects))
        if request.user.is_authenticated:
            done_list = Todo.objects.filter(
                user_todo=request.user.server_user,
                is_done=True,
            ).all()
            done_list = [i.homework_todo.first().id for i in done_list]
        else:
            done_list = []

        info_class = (
            Homework.objects.filter(group=-1, grade=grade, letter=letter)
            .prefetch_related("images", "files")
            .order_by("-created_at")
            .only()
            .first()
        )
        info_school = (
            Homework.objects.filter(group=-3)
            .prefetch_related("images", "files")
            .order_by("-created_at")
            .first()
        )
        if info_school:
            info_school.author = "Администрация"
        if not request.user.is_staff:
            info = [info_school, info_class]
        else:
            info_admin = (
                Homework.objects.filter(group=-2)
                .prefetch_related("images", "files")
                .order_by("-created_at")
                .first()
            )
            info = [info_school, info_admin, info_class]
        return render(
            request,
            "homework/homework.html",
            context={
                "homework": data,
                "empty_hw": null_subjects,
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
                    .only("subject", "author", "description", "created_at")
                    .prefetch_related("images", "files")
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
                    .only("subject", "author", "description", "created_at")
                    .prefetch_related("images", "files")
                    .order_by("group", "-subject", "-created_at")
                    .all()
                )
        except Homework.DoesNotExist:
            pass
        for homework in data:
            homework.subject = get_name_from_abbreviation(homework.subject)
        return data


class WeekdayHomeworkPage(View):
    @staticmethod
    def get(request, weekday):
        checker = check_grade_letter(request)
        if checker[0] == "Error":
            return checker[1]
        weekday -= 1
        if weekday >= 7 or weekday < 0:
            messages.error(request, "Такого дня в неделе не существует")
            return redirect("homework:homework_page")
        grade, letter, group = checker[1]
        latest_homework_ids = (
            Homework.objects.filter(Q(group=0) | Q(group=group))
            .filter(
                grade=grade,
                letter=letter,
                subject=OuterRef("subject"),
                created_at=Subquery(
                    Homework.objects.filter(
                        subject=OuterRef("subject"),
                    )
                    .values("created_at")
                    .order_by("-created_at")[:1],
                ),
            )
            .values("id")
        )
        subjects = [
            i.subject
            for i in get_schedule_from_weekday(
                grade,
                letter,
                group,
                weekday + 1,
            )
        ]
        data = (
            Homework.objects.filter(
                id__in=latest_homework_ids,
                subject__in=subjects,
            )
            .order_by("subject")
            .prefetch_related("images", "files")
            .defer("grade", "letter", "group")
        )
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

        week_list = get_list_of_dates(grade)
        return render(
            request,
            "homework/weekday_homework.html",
            context={
                "homework": data,
                "done_list": done_list,
                "weekday": week_list[weekday],
            },
        )


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
        user_subjects = get_user_subjects(
            grade,
            letter,
            group,
        )
        if isinstance(user_subjects, dict):
            messages.error(
                request,
                f"В {user_subjects['grade']} классе нет"
                f" литеры {user_subjects['letter']}",
            )
            return redirect("homework:choose_grad_let")
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
            if isinstance(response_list, dict):
                messages.error(
                    request,
                    f"В {response_list['grade']} классе нет"
                    f" литеры {response_list['letter']}",
                )
                return redirect("homework:homework_page")
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
        files_list_for_model = save_files(
            request_files_list,
            request.user.server_user.grade,
            request.user.server_user.letter,
        )
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
            author=f"{request.user.first_name} {request.user.last_name}",
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
            if isinstance(user_subjects, dict):
                messages.error(
                    request,
                    f"В {user_subjects['grade']} классе нет"
                    f" литеры {user_subjects['letter']}",
                )
                return redirect("homework:homework_page")
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
            files_list_for_model = save_files(
                request_files_list,
                request.user.server_user.grade,
                request.user.server_user.letter,
            )
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
        if not request.user.is_staff:
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
            if not request.user.is_superuser:
                messages.error(
                    request,
                    "Недостаточно прав дял совершения действия",
                )
                return redirect("homework:homework_page")
            group = -2
        else:
            if not request.user.is_superuser:
                messages.error(
                    request,
                    "Недостаточно прав дял совершения действия",
                )
                return redirect("homework:homework_page")
            group = -3
        request_files_list = request.FILES.getlist("files")
        files_list_for_model = save_files(
            request_files_list,
            request.user.server_user.grade,
            request.user.server_user.letter,
        )
        if files_list_for_model[0] == "Error":
            render(
                request,
                "homework/add_homework.html",
                context={
                    "errors": "Unsupported file format",
                },
            )
        files_list_for_model = files_list_for_model[1]
        if group != -1:
            homework_object = Homework.objects.create(
                description=description,
                grade=0,
                letter="",
                subject="info",
                group=group,
                author=f"{request.user.first_name} {request.user.last_name}",
            )
        else:
            homework_object = Homework.objects.create(
                description=description,
                grade=request.user.server_user.grade,
                letter=request.user.server_user.letter,
                subject="info",
                group=group,
                author=f"{request.user.first_name} {request.user.last_name}",
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
            files_list_for_model = save_files(
                request_files_list,
                request.user.server_user.grade,
                request.user.server_user.letter,
            )
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
        request.session["open_id"] = homework_id
        return redirect(reverse("homework:homework_page") + f"#{homework_id}")


class SchedulePage(generic.ListView):
    model = Schedule
    template_name = "homework/schedule.html"

    def dispatch(self, request, *args, **kwargs):
        checker = check_grade_letter(request)
        if checker[0] == "Error":
            return checker[1]
        self.grade, self.letter, self.group = checker[1]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        schedule = (
            Schedule.objects.filter(grade=self.grade, letter=self.letter)
            .filter(Q(group=self.group) | Q(group=0))
            .order_by("weekday", "lesson")
            .only("lesson", "subject", "weekday")
            .all()
        )
        for lesson in schedule:
            lesson.subject = get_name_from_abbreviation(lesson.subject)
        return schedule
