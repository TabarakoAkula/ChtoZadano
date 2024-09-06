import json

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import OuterRef, Q, Subquery
from django.shortcuts import redirect, render, reverse
from django.views import generic, View

from homework.api.serializers import (
    HomeworkSerializer,
    UserNotificationsSerializer,
)
from homework.forms import ChooseGradLetForm
from homework.models import File, Homework, Image, Schedule, Todo
from homework.utils import (
    add_notification,
    celery_add_notification,
    check_grade_letter,
    get_abbreviation_from_name,
    get_group_from_teacher,
    get_list_of_dates,
    get_name_from_abbreviation,
    get_schedule_from_weekday,
    get_user_subjects,
    redis_delete_data,
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
        data = cache.get(f"homework_page_data_{grade}_{letter}_{group}")
        if not data:
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
            cache.set(
                f"homework_page_data_{grade}_{letter}_{group}",
                data,
                timeout=600,
            )
        data_subjects = []
        for homework_obj in data:
            abbreviation = get_name_from_abbreviation(homework_obj.subject)
            abbreviation = f"{abbreviation[0].upper()}{abbreviation[1:]}"
            homework_obj.subject = abbreviation
            data_subjects.append(abbreviation)
        real_subjects = cache.get(f"user_subjects_{grade}_{letter}_{group}")
        if not real_subjects:
            real_subjects = get_user_subjects(grade, letter, group)
            cache.set(
                f"user_subjects_{grade}_{letter}_{group}",
                real_subjects,
                timeout=86400,
            )
        real_subjects = [f"{i[0].upper()}{i[1:]}" for i in real_subjects]
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
        info_class = cache.get(
            f"homework_page_info_class_{grade}_{letter}",
        )
        if not info_class:
            info_class = (
                Homework.objects.filter(group=-1, grade=grade, letter=letter)
                .prefetch_related("images", "files")
                .order_by("-created_at")
                .only()
                .first()
            )
            cache.set(
                f"homework_page_info_class_{grade}_{letter}",
                info_class,
                timeout=600,
            )
        info_school = cache.get("homework_page_info_school")
        if not info_school:
            info_school = (
                Homework.objects.filter(group=-3)
                .prefetch_related("images", "files")
                .order_by("-created_at")
                .first()
            )
            cache.set("homework_page_info_school", info_school, timeout=600)
        if info_school:
            info_school.author = "Администрация"
        if not request.user.is_staff:
            info = [info_school, info_class]
        else:
            info_admin = cache.get("homework_page_info_admin")
            if not info_admin:
                info_admin = (
                    Homework.objects.filter(group=-2)
                    .prefetch_related("images", "files")
                    .order_by("-created_at")
                    .first()
                )
                cache.set("homework_page_info_admin", info_school, timeout=600)
            info = [info_school, info_admin, info_class]
        dates = get_list_of_dates(grade)
        return render(
            request,
            "homework/homework.html",
            context={
                "homework": data,
                "empty_hw": null_subjects,
                "info": info,
                "done_list": done_list,
                "dates": dates,
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
            data = cache.get(
                f"all_homework_data_{self.grade}_{self.letter}_{self.group}",
            )
            if not data:
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
                cache.set(
                    f"all_homework_data_{self.grade}_"
                    f"{self.letter}_{self.group}",
                    data,
                    timeout=600,
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
        data = cache.get(
            f"weekday_page_data_{grade}_{letter}_{group}_{weekday}",
        )
        if not data:
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
            cache.set(
                f"weekday_page_data_{grade}_{letter}_{group}_{weekday}",
                data,
                timeout=600,
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
        info_class = cache.get(
            f"homework_page_info_class_{grade}_{letter}",
        )
        if not info_class:
            info_class = (
                Homework.objects.filter(group=-1, grade=grade, letter=letter)
                .prefetch_related("images", "files")
                .order_by("-created_at")
                .only()
                .first()
            )
            cache.set(
                f"homework_page_info_class_{grade}_{letter}",
                info_class,
                timeout=600,
            )
        info_school = cache.get("homework_page_info_school")
        if not info_school:
            info_school = (
                Homework.objects.filter(group=-3)
                .prefetch_related("images", "files")
                .order_by("-created_at")
                .first()
            )
            cache.set(
                "homework_page_info_school",
                info_school,
                timeout=600,
            )
        if info_school:
            info_school.author = "Администрация"
        if not request.user.is_staff:
            info = [info_school, info_class]
        else:
            info_admin = cache.get("homework_page_info_admin")
            if not info_admin:
                info_admin = (
                    Homework.objects.filter(group=-2)
                    .prefetch_related("images", "files")
                    .order_by("-created_at")
                    .first()
                )
                cache.set("homework_page_info_admin", info_admin, timeout=600)
            info = [info_school, info_admin, info_class]

        week_list = get_list_of_dates(grade)
        current_weekday = week_list[weekday]
        return render(
            request,
            "homework/weekday_homework.html",
            context={
                "homework": data,
                "done_list": done_list,
                "dates": week_list,
                "info": info,
                "current_weekday": current_weekday,
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
        grade = int(request.POST.get("grade"))
        letter = request.POST.get("letter")
        teacher = request.POST.get("group").replace("_", " ")
        group = get_group_from_teacher(teacher, grade, letter)
        if group == 0:
            messages.error(
                request,
                f"{teacher} не ведет в {grade}{letter} классе",
            )
            return redirect("homework:choose_grad_let")
        data = {
            "grade": grade,
            "letter": letter,
            "group": group,
        }
        user_subjects = cache.get(f"user_subjects_{grade}_{letter}_{group}")
        if not user_subjects:
            user_subjects = get_user_subjects(
                grade,
                letter,
                group,
            )
            cache.set(
                f"user_subjects_{grade}_{letter}_{group}",
                user_subjects,
                timeout=86400,
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
            response_list = cache.get(
                f"user_subjects_{grade}_{letter}_{group}",
            )
            if not response_list:
                response_list = get_user_subjects(grade, letter, group)
                cache.set(
                    f"user_subjects_{grade}_{letter}_{group}",
                    response_list,
                    timeout=86400,
                )
            if isinstance(response_list, dict):
                messages.error(
                    request,
                    f"В {response_list['grade']} классе нет"
                    f" литеры {response_list['letter']}",
                )
                return redirect("homework:homework_page")

            response_list = [f"{i[0].upper()}{i[1:]}" for i in response_list]
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
        if request.user.is_staff or request.user.is_superuser:
            pass
        else:
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
            subject,
        )
        files_list_for_model = files_list_for_model[1]
        server_user = request.user.server_user
        use_groups = False
        if subject not in [
            "eng1",
            "eng2",
            "ger1",
            "ger2",
            "ikt1",
            "ikt2",
        ]:
            use_groups = True
            group = 0
        else:
            group = server_user.group
        grade, letter = server_user.grade, server_user.letter
        homework_object = Homework.objects.create(
            description=description,
            grade=grade,
            letter=letter,
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
        homework_object.subject = get_name_from_abbreviation(
            homework_object.subject,
        )
        user = request.user.server_user
        if settings.USE_CELERY:
            celery_add_notification.delay(
                HomeworkSerializer(homework_object).data,
                UserNotificationsSerializer(user).data,
            )
        else:
            add_notification(
                HomeworkSerializer(homework_object).data,
                user,
                use_groups,
            )
        redis_delete_data(True, grade, letter, group)
        return redirect("homework:homework_page")


class EditHomework(View):
    @staticmethod
    def get(request, homework_id):
        if request.user.is_staff or request.user.is_superuser:
            request_user = request.user.server_user
            grade, letter, group = (
                request_user.grade,
                request_user.letter,
                request_user.group,
            )
            user_subjects = cache.get(
                f"user_subjects_{grade}_{letter}_{group}",
            )
            if not user_subjects:
                user_subjects = get_user_subjects(grade, letter, group)
                cache.set(
                    f"user_subjects_{grade}_{letter}_{group}",
                    user_subjects,
                    timeout=86400,
                )
            if isinstance(user_subjects, dict):
                messages.error(
                    request,
                    f"В {user_subjects['grade']} классе нет"
                    f" литеры {user_subjects['letter']}",
                )
                return redirect("homework:homework_page")
            group = request.user.server_user.group
            user_subjects = [f"{i[0].upper()}{i[1:]}" for i in user_subjects]
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
            server_user = request.user.server_user
            grade, letter = server_user.grade, server_user.letter
            group = server_user.group
            files_list_for_model = save_files(
                request_files_list,
                grade,
                letter,
                subject,
            )
            if files_list_for_model[0] == "Error":
                messages.error(request, "Неподходящий формат файла")
                return redirect(
                    "homework:edit_homework",
                    homework_id=homework_id,
                )
            files_list_for_model = files_list_for_model[1]
            try:
                homework_object = Homework.objects.get(
                    id=homework_id,
                    grade=grade,
                    letter=letter,
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
            redis_delete_data(True, grade, letter, group)
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
            grade, letter = request_user.grade, request_user.letter
            group = request_user.group
            try:
                hw_object = Homework.objects.get(
                    id=homework_id,
                    grade=grade,
                    letter=letter,
                )
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            if r_type == "img":
                Image.objects.get(id=file_id, homework=hw_object).delete()
            elif r_type == "file":
                File.objects.get(id=file_id, homework=hw_object).delete()
            messages.success(request, "Успешно обновлено")
            redis_delete_data(True, grade, letter, group)
            if hw_object.group in [-3, -2, -1]:
                return redirect(
                    "homework:edit_mailing",
                    homework_id=homework_id,
                )
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
            hw_info.subject = get_name_from_abbreviation(hw_info.subject)
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
            grade, letter = request_user.grade, request_user.letter
            group = request_user.group
            try:
                Homework.objects.get(
                    id=homework_id,
                    grade=grade,
                    letter=letter,
                ).delete()
            except Homework.DoesNotExist:
                messages.error(request, "Такой записи не существует")
                return redirect("homework:homework_page")
            messages.success(request, "Домашнее задание успешно удалено")
            redis_delete_data(True, grade, letter, group)
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
        grade = request.user.server_user.grade
        letter = request.user.server_user.letter
        files_list_for_model = save_files(
            request_files_list,
            grade,
            letter,
            "info",
        )
        if files_list_for_model[0] == "Error":
            messages.error(request, "Неподходящий формат файла")
            return render(
                request,
                "homework/add_homework.html",
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
                grade=grade,
                letter=letter,
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
        add_notification.delay(
            homework_object,
            request.user.server_user,
            False,
        ).delay()
        redis_delete_data(False, grade, letter, group)
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
            grade = request.user.server_user.grade
            letter = request.user.server_user.letter
            files_list_for_model = save_files(
                request_files_list,
                grade,
                letter,
                "info",
            )
            if files_list_for_model[0] == "Error":
                messages.error(request, "Неподходящий формат файла")
                return render(
                    request,
                    "homework/add_homework.html",
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
            redis_delete_data(False, grade, letter, group)
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
            redis_delete_data(
                False,
                request.user.server_user.grade,
                request.user.server_user.letter,
                request.user.server_user.group,
            )
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
            redis_delete_data(
                False,
                request.user.server_user.grade,
                request.user.server_user.letter,
                request.user.server_user.group,
            )
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
        request.session["mark_done"] = not todo_obj.is_done
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
        schedule = cache.get(
            f"schedule_{self.grade}_{self.letter}_{self.group}",
        )
        if not schedule:
            schedule = (
                Schedule.objects.filter(grade=self.grade, letter=self.letter)
                .filter(Q(group=self.group) | Q(group=0))
                .order_by("weekday", "lesson")
                .only("lesson", "subject", "weekday")
                .all()
            )
            cache.set(
                f"schedule_{self.grade}_{self.letter}_{self.group}",
                schedule,
                timeout=86400,
            )
        for lesson in schedule:
            lesson.subject = get_name_from_abbreviation(lesson.subject)
        return schedule
