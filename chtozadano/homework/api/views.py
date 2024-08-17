from datetime import datetime, timedelta

from django.db.models import OuterRef, Q, Subquery
from rest_framework import response, viewsets
from rest_framework.views import APIView

from homework.api.serializers import HomeworkSerializer, ScheduleSerializer
from homework.models import File, Homework, Image, Schedule, Todo
from homework.utils import (
    get_abbreviation_from_name,
    get_name_from_abbreviation,
    get_tomorrow_schedule,
    get_user_subjects,
)
import users.models


class GetLastHomeworkAllSubjectsAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeworkSerializer

    def get_homework(self, request):
        try:
            user = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        latest_homework_ids = (
            Homework.objects.filter(Q(group=0) | Q(group=user.group))
            .filter(
                grade=user.grade,
                letter=user.letter,
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
        for homework_obj in data:
            homework_obj.subject = get_name_from_abbreviation(
                homework_obj.subject,
            )
        homework = self.get_serializer(data, many=True).data
        return response.Response(homework)


class GetOneSubjectAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeworkSerializer

    def get_homework(self, request):
        try:
            use_abbreviation = request.data["use_abbreviation"]
        except KeyError:
            use_abbreviation = False
        try:
            user = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            grade = user.grade
            letter = user.letter
            group = user.group
            subject = request.data["subject"]
            if use_abbreviation:
                if subject in [
                    "ikt",
                    "eng",
                    "ger",
                ]:
                    subject += str(group)
                subject = get_name_from_abbreviation(subject).lower()
            user_subjects = get_user_subjects(grade, letter, group)
            if subject not in user_subjects:
                return response.Response(
                    {
                        "empty": "Not in subjects",
                    },
                    status=406,
                )
            abr_subject = get_abbreviation_from_name(subject)
            hw_object = (
                Homework.objects.filter(
                    grade=grade,
                    letter=letter,
                    subject=abr_subject,
                )
                .filter(Q(group=group) | Q(group=0))
                .order_by("-created_at")
                .first()
            )
        except Homework.DoesNotExist:
            return response.Response({"error": "Does not exist"}, status=404)
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if not hw_object:
            return response.Response(
                {
                    "empty": "Does not exist",
                    "subject": subject,
                },
                status=404,
            )
        hw_object.subject = subject
        serialized = self.get_serializer(hw_object)
        return response.Response(serialized.data)


class GetAllHomeworkFromDateAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeworkSerializer

    def get_homework(self, request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            date = request.data["date"].split(".")
            year, month, day = list(map(int, date))
        except (KeyError, ValueError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        latest_homework_ids = (
            Homework.objects.filter(Q(group=0) | Q(group=user_obj.group))
            .filter(
                grade=user_obj.grade,
                letter=user_obj.letter,
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
            .filter(created_at__date=datetime(year, month, day))
            .order_by("subject")
            .prefetch_related("images", "files")
            .defer("grade", "letter", "group")
        )
        for homework_obj in data:
            homework_obj.subject = get_name_from_abbreviation(
                homework_obj.subject,
            )
        homework = self.get_serializer(data, many=True)
        return response.Response(homework.data)


class GetHomeworkFromIdAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeworkSerializer

    def get_homework(self, request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            grade = user_obj.grade
            letter = user_obj.letter
            group = user_obj.group
            homework_id = request.data["homework_id"]
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
            return response.Response({"error": "Does not exist"}, status=404)
        except (KeyError, ValueError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if hw_object:
            homework = self.get_serializer(hw_object)
            return response.Response(homework.data)
        return response.Response({"error": "Undefined"})


class GetTomorrowHomeworkAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeworkSerializer

    def get_homework(self, request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        schedule = get_tomorrow_schedule(
            user_obj.grade,
            user_obj.letter,
            user_obj.group,
        )
        data = {}
        for lesson in schedule:
            try:
                homework_obj = (
                    Homework.objects.filter(
                        Q(group=0) | Q(group=user_obj.group),
                    )
                    .filter(
                        grade=user_obj.grade,
                        letter=user_obj.letter,
                        subject=lesson.subject,
                    )
                    .order_by("-created_at")
                    .first()
                )
            except Homework.DoesNotExist:
                data[lesson.lesson] = None
            else:
                if homework_obj:
                    homework_obj.subject = get_name_from_abbreviation(
                        homework_obj.subject,
                    )
                    serialized_obj = self.get_serializer(homework_obj).data
                    data[lesson.lesson] = serialized_obj
                    data[lesson.lesson]["data"] = True
                else:
                    data[lesson.lesson] = {}
                    data[lesson.lesson][
                        "subject"
                    ] = get_name_from_abbreviation(lesson.subject)
                    data[lesson.lesson]["data"] = False
        return response.Response(data)


class AddHomeWorkAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            grade = user_obj.grade
            letter = user_obj.letter
            subject = request.data["subject"]
            description = request.data["description"]
            images = request.data["images"]
            files = request.data["files"]
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if subject not in ["eng1", "eng2", "ger1", "ger2", "ikt1", "ikt2"]:
            group = 0
        else:
            group = user_obj.group
        hw_object = Homework.objects.create(
            grade=grade,
            letter=letter,
            description=description,
            group=group,
            subject=get_abbreviation_from_name(subject),
            author=f"{django_user.first_name} {django_user.last_name}",
        )
        for image in images:
            path = image["path"]
            tg_id = image["telegram_file_id"]
            hw_object.images.add(
                Image.objects.create(
                    image=path,
                    telegram_file_id=tg_id,
                ),
            )
        for file in files:
            path = file["path"]
            tg_id = file["telegram_file_id"]

            hw_object.files.add(
                File.objects.create(
                    file=path,
                    telegram_file_id=tg_id,
                    file_name=path.split("/")[-1],
                ),
            )
        return response.Response(
            {
                "success": "Successful",
                "homework_id": hw_object.id,
            },
        )


class EditHomeworkDescriptionAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            homework_id = request.data["homework_id"]
            new_description = request.data["description"]
            grade = user_obj.grade
            letter = user_obj.letter
            group = user_obj.group
            homework_obj = Homework.objects.filter(
                Q(group=0) | Q(group=group),
            ).get(id=homework_id, grade=grade, letter=letter)
        except Homework.DoesNotExist:
            return response.Response({"error": "Does not exist"}, status=404)
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        homework_obj.description = new_description
        homework_obj.save()
        return response.Response({"success": "Successful"})


class EditHomeworkImagesAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            homework_id = request.data["homework_id"]
            new_images = request.data["images"]
            grade = user_obj.grade
            letter = user_obj.letter
            group = user_obj.group
            homework_obj = Homework.objects.filter(
                Q(group=0) | Q(group=group),
            ).get(id=homework_id, grade=grade, letter=letter)
            Image.objects.filter(homework_id=homework_id).delete()
        except Homework.DoesNotExist:
            return response.Response({"error": "Does not exist"}, status=404)
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        for image in new_images:
            path = image["path"]
            tg_id = image["telegram_file_id"]
            image_object = Image.objects.create(
                image=path,
                telegram_file_id=tg_id,
            )
            homework_obj.images.add(image_object)
        return response.Response({"success": "Successful"})


class EditHomeworkFilesAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            homework_id = request.data["homework_id"]
            new_files = request.data["files"]
            grade = user_obj.grade
            letter = user_obj.letter
            group = user_obj.group
            homework_obj = Homework.objects.filter(
                Q(group=0) | Q(group=group),
            ).get(id=homework_id, grade=grade, letter=letter)
            File.objects.filter(homework_id=homework_id).delete()
        except Homework.DoesNotExist:
            return response.Response({"error": "Does not exist"}, status=404)
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        for file in new_files:
            path = file["path"]
            tg_id = file["telegram_file_id"]
            file_object = File.objects.create(
                file=path,
                telegram_file_id=tg_id,
            )
            file_name = path.split("/")[-1]
            file_object.file_name = file_name
            file_object.save()
            homework_obj.files.add(file_object)
        return response.Response({"success": "Successful"})


class DeleteHomeworkAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            user_grade = user_obj.grade
            user_letter = user_obj.letter
            user_group = user_obj.group
            homework_id = request.data["homework_id"]
            Homework.objects.filter(Q(group=user_group) | Q(group=0)).get(
                grade=user_grade,
                letter=user_letter,
                id=homework_id,
            ).delete()
        except Homework.DoesNotExist:
            return response.Response({"error": "Does not exist"}, status=404)
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"success": "Successful"})


class GetMailingAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeworkSerializer

    def get_mailing(self, request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            data = {}
            info_obj_one = (
                Homework.objects.filter(group=-1)
                .order_by("-created_at")
                .first()
            )
            info_obj_two = (
                Homework.objects.filter(group=-3)
                .order_by("-created_at")
                .first()
            )
            data["class"] = self.get_serializer(info_obj_one).data
            data["school"] = self.get_serializer(info_obj_two).data
            if django_user.is_staff or django_user.is_superuser:
                info_obj_three = (
                    Homework.objects.filter(group=-2)
                    .order_by("-created_at")
                    .first()
                )
                data["admins"] = HomeworkSerializer(info_obj_three).data
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response(data)


class AddMailingAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            level = request.data["level"]
            if level == "class":
                if not django_user.is_staff:
                    return response.Response(
                        {"error": "Not allowed"},
                        status=403,
                    )
                grade = user_obj.grade
                letter = user_obj.letter
                images = request.data["images"]
                files = request.data["files"]
                homework_obj = Homework.objects.create(
                    grade=grade,
                    letter=letter,
                    author=f"{django_user.first_name} {django_user.last_name}",
                )
                for image in images:
                    path = image["path"]
                    tg_id = image["telegram_file_id"]
                    image_obj = Image.objects.create(
                        image=path,
                        telegram_file_id=tg_id,
                    )
                    homework_obj.images.add(image_obj)
                for file in files:
                    path = file["path"]
                    tg_id = file["telegram_file_id"]
                    file_obj = File.objects.create(
                        file=path,
                        telegram_file_id=tg_id,
                        file_name=path.split("/")[-1],
                    )
                    homework_obj.files.add(file_obj)
                homework_obj.group = -1
                homework_obj.description = request.data["description"]
                homework_obj.subject = "info"
                homework_obj.save()
                return response.Response({"success": "Successful"})
            if not django_user.is_superuser:
                return response.Response({"error": "Not allowed"}, status=403)
            grade = 0
            letter = ""
            images = request.data["images"]
            files = request.data["files"]
            homework_obj = Homework.objects.create(
                grade=grade,
                letter=letter,
                author="Администрация сайта",
            )
            for image in images:
                path = image["path"]
                tg_id = image["telegram_file_id"]
                image_obj = Image.objects.create(
                    image=path,
                    telegram_file_id=tg_id,
                )
                homework_obj.images.add(image_obj)
            for file in files:
                path = file["path"]
                tg_id = file["telegram_file_id"]
                file_obj = File.objects.create(
                    file=path,
                    telegram_file_id=tg_id,
                    file_name=path.split("/")[-1],
                )
                homework_obj.files.add(file_obj)
            if level == "admins":
                homework_obj.group = -2
            elif level == "school":
                homework_obj.group = -3
            homework_obj.description = request.data["description"]
            homework_obj.subject = "info"
            homework_obj.author = (
                f"{django_user.first_name} {django_user.last_name}"
            )
            homework_obj.save()
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"success": "Successful"})


class EditMailingAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            homework_id = request.data["homework_id"]
            if django_user.is_superuser:
                homework_obj = Homework.objects.filter(
                    Q(group=-1) | Q(group=-2) | Q(group=-3),
                ).get(id=homework_id)
            elif django_user.is_staff:
                homework_obj = Homework.objects.filter(group=-1).get(
                    id=homework_id,
                )
            else:
                return response.Response({"error": "Not allowed"}, status=403)
        except Homework.DoesNotExist:
            return response.Response(
                {"error": "Does not exist | Not allowed"},
                status=404,
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if homework_obj:
            serialized_data = HomeworkSerializer(homework_obj).data
            images = [i.image.url for i in homework_obj.images.all()]
            files = [i.file.url for i in homework_obj.files.all()]
            serialized_data["images"] = images
            serialized_data["files"] = files
            return response.Response(serialized_data)
        return response.Response(
            {"error": "Does not exist | Not allowed"},
            status=404,
        )


class EditMailingDescriptionAPI(APIView):
    @staticmethod
    def post(request):
        try:
            telegram_id = request.data["telegram_id"]
            user_obj = users.models.User.objects.get(telegram_id=telegram_id)
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            homework_id = request.data["homework_id"]
            new_description = request.data["description"]
            homework_obj = None
            if django_user.is_superuser:
                homework_obj = Homework.objects.get(id=homework_id)
            elif django_user.is_staff:
                homework_obj = Homework.objects.filter(group=-1).get(
                    id=homework_id,
                )
        except Homework.DoesNotExist:
            return response.Response(
                {"error": "Does not exist | Not allowed"},
                status=404,
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if not homework_obj:
            return response.Response({"error": "Error"})
        homework_obj.description = new_description
        homework_obj.save()
        return response.Response({"success": "Successful"})


class EditMailingImagesAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            homework_id = request.data["homework_id"]
            new_images = request.data["images"]
            if django_user.is_superuser:
                homework_obj = Homework.objects.get(id=homework_id)
                Image.objects.filter(homework_id=homework_id).delete()
            elif django_user.is_staff:
                homework_obj = Homework.objects.get(id=homework_id, group=-1)
                Image.objects.filter(homework_id=homework_id).delete()
        except Homework.DoesNotExist:
            return response.Response(
                {"error": "Does not exist | Not allowed"},
                status=404,
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        for image in new_images:
            path = image["path"]
            tg_id = image["telegram_file_id"]
            image_object = Image.objects.create(
                image=path,
                telegram_file_id=tg_id,
            )
            homework_obj.images.add(image_object)
        return response.Response({"success": "Successful"})


class EditMailingFilesAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            homework_id = request.data["homework_id"]
            new_files = request.data["files"]
            if django_user.is_superuser:
                homework_obj = Homework.objects.get(id=homework_id)
                File.objects.filter(homework_id=homework_id).delete()
            elif django_user.is_staff:
                homework_obj = Homework.objects.get(id=homework_id, group=-1)
                File.objects.filter(homework_id=homework_id).delete()
        except Homework.DoesNotExist:
            return response.Response(
                {"error": "Does not exist | Not allowed"},
                status=404,
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        for file in new_files:
            path = file["path"]
            tg_id = file["telegram_file_id"]
            file_object = File.objects.create(
                file=path,
                telegram_file_id=tg_id,
                file_name=path.split("/")[-1],
            )
            file_name = path.split("/")[-1]
            file_object.file_name = file_name
            file_object.save()
            homework_obj.files.add(file_object)
        return response.Response({"success": "Successful"})


class DeleteMailingAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            django_user = user_obj.user
            if not django_user.is_staff:
                return response.Response({"error": "Not allowed"}, status=403)
            homework_id = request.data["homework_id"]
            if django_user.is_superuser:
                Homework.objects.get(
                    id=homework_id,
                ).delete()
            elif django_user.is_staff:
                Homework.objects.get(
                    group=-1,
                    id=homework_id,
                ).delete()
        except Homework.DoesNotExist:
            return response.Response(
                {"error": "Does not exist | Not allowed"},
                status=404,
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response({"success": "Successful"})


class TodoWorkAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            homework_id = request.data["homework_id"]
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        try:
            homework_obj = Homework.objects.get(id=homework_id)
            homework_todo = Todo.objects.get(
                user_todo=user_obj,
                homework_todo=homework_obj,
            )
        except Homework.DoesNotExist:
            return response.Response({"error": "Bad request data"}, status=400)
        except Todo.DoesNotExist:
            todo_obj = Todo.objects.create()
            todo_obj.user_todo.add(user_obj)
            todo_obj.homework_todo.add(homework_obj)
            todo_obj.is_done = True
            todo_obj.save()
        else:
            homework_todo.is_done = not homework_todo.is_done
            homework_todo.save()
        return response.Response({"success": "Successful"})


class GetTomorrowScheduleAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduleSerializer

    def get_schedule(self, request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            schedule = get_tomorrow_schedule(
                user_obj.grade,
                user_obj.letter,
                user_obj.group,
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        for lesson in schedule:
            lesson.subject = get_name_from_abbreviation(lesson.subject)
        return response.Response(self.get_serializer(schedule, many=True).data)


class DeleteOldHomeworkAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        if not user_obj.user.is_superuser:
            return response.Response({"error": "Not allowed ^)"}, status=403)

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
        return response.Response({"success": response_message})


class AddScheduleAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user_obj = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            if not user_obj.user.is_superuser:
                return response.Response({"error": "Not allowed"}, status=403)
            grade = request.data["grade"]
            letter = request.data["letter"]
            weekday = request.data["weekday"]
            lesson = request.data["lesson"]
            subject = request.data["subject"]
            group = request.data["group"]
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        Schedule.objects.create(
            grade=grade,
            letter=letter,
            group=group,
            weekday=weekday,
            subject=subject,
            lesson=lesson,
        )
        return response.Response({"success": "Successful"})


class GetWeekScheduleAPI(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduleSerializer

    def get_schedule(self, request):
        try:
            user = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        latest_schedule_ids = (
            Schedule.objects.filter(Q(group=0) | Q(group=user.group))
            .filter(
                grade=user.grade,
                letter=user.letter,
                weekday=OuterRef("weekday"),
            )
            .values("id")
        )
        data = Schedule.objects.filter(id__in=latest_schedule_ids).order_by(
            "weekday",
            "lesson",
        )
        for schedule_obj in data:
            schedule_obj.subject = get_name_from_abbreviation(
                schedule_obj.subject,
            )
        return response.Response(self.get_serializer(data, many=True).data)


class GetUserSubjects(APIView):
    @staticmethod
    def post(request):
        try:
            user = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        user_subjects = get_user_subjects(user.grade, user.letter, user.group)
        return response.Response(user_subjects)


class CreatePathAPI(APIView):
    @staticmethod
    def post(request):
        try:
            user = users.models.User.objects.get(
                telegram_id=request.data["telegram_id"],
            )
            subject = request.data["subject"]
        except (KeyError, users.models.User.DoesNotExist):
            return response.Response({"error": "Bad request data"}, status=400)
        return response.Response(
            {
                "abbreviation": get_abbreviation_from_name(subject),
                "grade": user.grade,
                "letter": user.letter,
            },
        )
