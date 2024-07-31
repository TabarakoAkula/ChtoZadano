from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Q
from parameterized import parameterized
from rest_framework.test import APIClient, APITestCase

from homework.models import Homework, Todo
from users.models import User

client = APIClient()


class HomeworkAPITests(APITestCase):
    multi_db = True
    fixtures = ["fixtures/test_api_data.json"]

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 200),
        ],
    )
    def test_get_all_subjects(self, data, status_code):
        response = client.post(
            "/api/v1/get_last_homework_all_subjects/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "subject": ""}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "subject": "",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "subject": "rus",
                },
                404,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "subject": "Русский язык",
                },
                200,
            ),
        ],
    )
    def test_get_one_subject(self, data, status_code):
        response = client.post(
            "/api/v1/get_homework_for_subject/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "subject": ""}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "date": "",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "date": "rus",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "date": "2024.07.28",
                },
                200,
            ),
        ],
    )
    def test_get_homework_from_date(self, data, status_code):
        response = client.post(
            "/api/v1/get_homework_from_date/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "homework_id": 1}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "homework_id": 1,
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "homework_id": "rus",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "homework_id": 1,
                },
                200,
            ),
        ],
    )
    def test_get_homework_from_id(self, data, status_code):
        response = client.post(
            "/api/v1/get_homework_from_id/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "1234"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "1234", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 200),
        ],
    )
    def test_tomorrow_homework(self, data, status_code):
        response = client.post(
            "/api/v1/get_tomorrow_homework/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "subject": "Русский язык",
                    "description": "Описание",
                    "images": ["test_path/test_image.jpg"],
                    "files": ["test_path/test_file.jpg"],
                    "author": "test_system",
                },
                200,
            ),
        ],
    )
    def test_add_homework(self, data, status_code):
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            first_counter = (
                Homework.objects.filter(
                    grade=user_obj.grade,
                    letter=user_obj.letter,
                )
                .filter(Q(group=0) | Q(group=user_obj.group))
                .count()
            )
        response = client.post(
            "/api/v1/add_homework/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_counter = (
                Homework.objects.filter(
                    grade=user_obj.grade,
                    letter=user_obj.letter,
                )
                .filter(Q(group=0) | Q(group=user_obj.group))
                .count()
            )
            self.assertEquals(first_counter + 1, second_counter)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 1,
                    "description": "Описание",
                },
                200,
            ),
        ],
    )
    def test_edit_homework_description(self, data, status_code):
        if status_code == 200:
            first_description = Homework.objects.get(
                id=data["homework_id"],
            ).description
        response = client.post(
            "/api/v1/edit_homework_description/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_description = Homework.objects.get(
                id=data["homework_id"],
            ).description
            self.assertNotEquals(data["description"], first_description)
            self.assertEquals(data["description"], second_description)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 1,
                    "images": ["new_path_1", "new_path_2"],
                },
                200,
            ),
        ],
    )
    def test_edit_homework_images(self, data, status_code):
        if status_code == 200:
            first_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).images.values_list("image")
            ]
        response = client.post(
            "/api/v1/edit_homework_images/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).images.values_list("image")
            ]
            self.assertNotEquals(data["images"], first_description)
            self.assertEquals(data["images"], second_description)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 1,
                    "files": ["new_path_1", "new_path_2"],
                },
                200,
            ),
        ],
    )
    def test_edit_homework_files(self, data, status_code):
        if status_code == 200:
            first_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).files.values_list("file")
            ]
        response = client.post(
            "/api/v1/edit_homework_files/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).files.values_list("file")
            ]
            self.assertNotEquals(data["files"], first_description)
            self.assertEquals(data["files"], second_description)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 1,
                },
                200,
            ),
        ],
    )
    def test_delete_homework(self, data, status_code):
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            first_counter = (
                Homework.objects.filter(
                    grade=user_obj.grade,
                    letter=user_obj.letter,
                )
                .filter(Q(group=0) | Q(group=user_obj.group))
                .count()
            )
        response = client.post(
            "/api/v1/delete_homework/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_counter = (
                Homework.objects.filter(
                    grade=user_obj.grade,
                    letter=user_obj.letter,
                )
                .filter(Q(group=0) | Q(group=user_obj.group))
                .count()
            )
            self.assertEquals(first_counter - 1, second_counter)

    @parameterized.expand(
        [
            ({"api_key": "1235"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "1235", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 200),
        ],
    )
    def test_get_mailing(self, data, status_code):
        response = client.post(
            "/api/v1/get_mailing/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "1231"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "1231", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "description": "Описание",
                    "level": "class",
                    "images": ["test_path/test_image.jpg"],
                    "files": ["test_path/test_file.jpg"],
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "description": "Описание",
                    "level": "school",
                    "images": ["test_path/test_image.jpg"],
                    "files": ["test_path/test_file.jpg"],
                },
                403,
            ),
        ],
    )
    def test_add_mailing(self, data, status_code):
        if status_code == 200:
            first_counter = Homework.objects.filter(
                Q(group=-1) | Q(group=-3),
            ).count()
        response = client.post(
            "/api/v1/add_mailing/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_counter = Homework.objects.filter(
                Q(group=-1) | Q(group=-3),
            ).count()
            self.assertEquals(first_counter + 1, second_counter)

    @parameterized.expand(
        [
            ({"api_key": "11235"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "11235", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "homework_id": 6,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "homework_id": 7,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 6,
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 7,
                },
                404,
            ),
        ],
    )
    def test_edit_mailing(self, data, status_code):
        response = client.post(
            "/api/v1/edit_mailing/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "112314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "112314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 6,
                    "description": "Описание",
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 7,
                    "description": "Описание",
                },
                404,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                    "homework_id": 7,
                    "description": "Описание",
                },
                200,
            ),
        ],
    )
    def test_edit_mailing_description(self, data, status_code):
        if status_code == 200:
            first_description = Homework.objects.get(
                id=data["homework_id"],
            ).description
        response = client.post(
            "/api/v1/edit_mailing_description/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_description = Homework.objects.get(
                id=data["homework_id"],
            ).description
            self.assertNotEquals(data["description"], first_description)
            self.assertEquals(data["description"], second_description)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 6,
                    "images": ["new_path_1", "new_path_2"],
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 7,
                    "images": ["new_path_1", "new_path_2"],
                },
                404,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                    "homework_id": 7,
                    "images": ["new_path_1", "new_path_2"],
                },
                200,
            ),
        ],
    )
    def test_edit_mailing_images(self, data, status_code):
        if status_code == 200:
            first_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).images.values_list("image")
            ]
        response = client.post(
            "/api/v1/edit_mailing_images/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).images.values_list("image")
            ]
            self.assertNotEquals(data["images"], first_description)
            self.assertEquals(data["images"], second_description)

    @parameterized.expand(
        [
            ({"api_key": "112314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "112314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 6,
                    "files": ["new_path_1", "new_path_2"],
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 7,
                    "files": ["new_path_1", "new_path_2"],
                },
                404,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                    "homework_id": 7,
                    "files": ["new_path_1", "new_path_2"],
                },
                200,
            ),
        ],
    )
    def test_edit_mailing_files(self, data, status_code):
        if status_code == 200:
            first_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).files.values_list("file")
            ]
        response = client.post(
            "/api/v1/edit_mailing_files/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_description = [
                i[0]
                for i in Homework.objects.get(
                    id=data["homework_id"],
                ).files.values_list("file")
            ]
            self.assertNotEquals(data["files"], first_description)
            self.assertEquals(data["files"], second_description)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 6,
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "homework_id": 7,
                },
                404,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                    "homework_id": 7,
                },
                200,
            ),
        ],
    )
    def test_delete_mailing(self, data, status_code):
        if status_code == 200:
            first_counter = Homework.objects.filter(
                group__in=[-1, -2, -3],
            ).count()
        response = client.post(
            "/api/v1/delete_mailing/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            second_counter = Homework.objects.filter(
                group__in=[-1, -2, -3],
            ).count()
            self.assertEquals(first_counter - 1, second_counter)

    @parameterized.expand(
        [
            ({"api_key": "12314"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "12314", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "homework_id": 2,
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "homework_id": 4,
                },
                200,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "homework_id": 999,
                },
                400,
            ),
        ],
    )
    def test_todo(self, data, status_code):
        if status_code == 200:
            homework_obj = Homework.objects.get(id=data["homework_id"])
            user_obj = User.objects.get(telegram_id=data["telegram_id"])
            todo_obj_1 = Todo.objects.filter(
                homework_todo=homework_obj,
                user_todo=user_obj,
            ).first()
            if todo_obj_1:
                response = client.post(
                    "/api/v1/change_todo/",
                    data=data,
                    format="json",
                )
                todo_obj_2 = Todo.objects.filter(
                    homework_todo=homework_obj,
                    user_todo=user_obj,
                ).first()
                self.assertEquals(todo_obj_1.is_done, not todo_obj_2.is_done)
            else:
                response = client.post(
                    "/api/v1/change_todo/",
                    data=data,
                    format="json",
                )
                todo_obj_2 = Todo.objects.filter(
                    homework_todo=homework_obj,
                    user_todo=user_obj,
                ).first()
                self.assertTrue(todo_obj_2)
        else:
            response = client.post(
                "/api/v1/change_todo/",
                data=data,
                format="json",
            )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "123411"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123411", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 200),
        ],
    )
    def test_tomorrow_schedule(self, data, status_code):
        response = client.post(
            "/api/v1/get_tomorrow_schedule/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "1123411"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "1123411", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 0}, 400),
            ({"api_key": settings.API_KEY, "telegram_id": 1}, 403),
            ({"api_key": settings.API_KEY, "telegram_id": 2}, 403),
            ({"api_key": settings.API_KEY, "telegram_id": 3}, 200),
        ],
    )
    def test_delete_old_homework(self, data, status_code):
        response = client.post(
            "/api/v1/delete_old_homework/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            today = datetime.today().date()
            two_weeks_ago = today - timedelta(days=14)
            todo_objects_2 = Todo.objects.filter(
                created_at__lt=two_weeks_ago,
            ).count()
            hw_objects_2 = Homework.objects.filter(
                created_at__lt=two_weeks_ago,
            ).count()
            self.assertEquals(todo_objects_2, 0)
            self.assertEquals(hw_objects_2, 0)
