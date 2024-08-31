from django.conf import settings
from parameterized import parameterized
from rest_framework.test import APIClient, APITestCase

from users.models import BecomeAdmin, User

client = APIClient()


class UsersAPITests(APITestCase):
    multi_db = True
    fixtures = ["fixtures/test_api_data.json"]

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "confirmation_code": "",
                    "name": "test_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "name": "test_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "confirmation_code": 123123,
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "confirmation_code": 123123,
                    "name": "test_name",
                },
                200,
            ),
        ],
    )
    def test_code_confirmation(self, data, status_code):
        response = client.post(
            "/api/v1/code_confirmation/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "group": 1,
                    "grade": 11,
                    "letter": "Б",
                    "name": "test_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "grade": 11,
                    "letter": "Б",
                    "name": "test_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "group": 1,
                    "letter": "Б",
                    "name": "test_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "group": 1,
                    "grade": 11,
                    "name": "test_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "group": 1,
                    "grade": 11,
                    "letter": "Б",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 0,
                    "group": 1,
                    "grade": 11,
                    "letter": "Б",
                    "name": "test_name",
                },
                200,
            ),
        ],
    )
    def test_create_user(self, data, status_code):
        response = client.post(
            "/api/v1/create_user/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_get_contacts(self, data, status_code):
        response = client.post(
            "/api/v1/get_contacts/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "first_name": "second_first_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "last_name": "second_last_name",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "first_name": "second_first_name",
                    "last_name": "second_last_name",
                },
                200,
            ),
        ],
    )
    def test_change_contacts(self, data, status_code):
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            first_name = user_obj.user.first_name
            last_name = user_obj.user.last_name
        response = client.post(
            "/api/v1/change_contacts/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            new_first_name = user_obj.user.first_name
            new_last_name = user_obj.user.last_name
            self.assertNotEquals(first_name, new_first_name)
            self.assertNotEquals(last_name, new_last_name)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_get_quotes(self, data, status_code):
        response = client.post(
            "/api/v1/get_quotes_status/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_change_quotes(self, data, status_code):
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            first_quotes = user_obj.show_quotes
        response = client.post(
            "/api/v1/change_quotes/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            second_quotes = user_obj.show_quotes
            self.assertNotEquals(first_quotes, second_quotes)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "grade": 11,
                    "letter": "Б",
                    "group": 1,
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "letter": "Б",
                    "group": 1,
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "grade": 11,
                    "group": 1,
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "grade": 11,
                    "letter": "Б",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "letter": "А",
                    "grade": 10,
                    "group": 2,
                },
                200,
            ),
        ],
    )
    def test_change_grade_letter(self, data, status_code):
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            grade, letter = user_obj.grade, user_obj.letter
            group = user_obj.group
        response = client.post(
            "/api/v1/change_grade_letter/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            new_grade, new_letter = user_obj.grade, user_obj.letter
            new_group = user_obj.group
            self.assertNotEquals(
                [grade, letter, group],
                [new_grade, new_letter, new_group],
            )

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_get_chat_mode(self, data, status_code):
        response = client.post(
            "/api/v1/get_chat_mode/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_change_chat_mode(self, data, status_code):
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            first_chat_mode = user_obj.chat_mode
        response = client.post(
            "/api/v1/change_chat_mode/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            user_obj = User.objects.get(
                telegram_id=data["telegram_id"],
            )
            second_chat_mode = user_obj.chat_mode
            self.assertNotEquals(first_chat_mode, second_chat_mode)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 4,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                },
                200,
            ),
        ],
    )
    def test_show_become_admin(self, data, status_code):
        response = client.post(
            "/api/v1/show_become_admin/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 4,
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 5,
                },
                200,
            ),
        ],
    )
    def test_become_admin(self, data, status_code):
        if status_code == 200:
            requests_before = BecomeAdmin.objects.count()
        response = client.post(
            "/api/v1/become_admin/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            requests_after = BecomeAdmin.objects.count()
            self.assertEquals(requests_before + 1, requests_after)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "candidate_id": 1,
                    "decision": "Б",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                    "decision": "Б",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                    "candidate_id": 1,
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                    "candidate_id": 1,
                    "decision": "decline",
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 2,
                    "candidate_id": 1,
                    "decision": "decline",
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 4,
                    "candidate_id": 1,
                    "decision": "decline",
                },
                403,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 3,
                    "candidate_id": 1,
                    "decision": "accept",
                },
                200,
            ),
        ],
    )
    def test_become_admin_decision(self, data, status_code):
        if status_code == 200:
            requests_before = BecomeAdmin.objects.count()
            user_obj = User.objects.get(telegram_id=data["candidate_id"])
            user_status_before = user_obj.user.is_staff
        response = client.post(
            "/api/v1/become_admin_accept_decline/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            requests_after = BecomeAdmin.objects.count()
            user_obj = User.objects.get(telegram_id=data["candidate_id"])
            user_status_after = user_obj.user.is_staff
            self.assertEquals(requests_before - 1, requests_after)
            self.assertNotEquals(user_status_before, user_status_after)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_is_user_in_system(self, data, status_code):
        response = client.post(
            "/api/v1/is_user_in_system/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_become_delete_user(self, data, status_code):
        if status_code == 200:
            requests_before = BecomeAdmin.objects.count()
        response = client.post(
            "/api/v1/become_admin_delete_user/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
        if status_code == 200:
            requests_after = BecomeAdmin.objects.count()
            self.assertEquals(requests_before - 1, requests_after)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "telegram_id": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_get_admins(self, data, status_code):
        response = client.post(
            "/api/v1/get_admins/",
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
            (
                {
                    "api_key": settings.API_KEY,
                    "telegram_id": 1,
                },
                200,
            ),
        ],
    )
    def test_is_user_admin(self, data, status_code):
        response = client.post(
            "/api/v1/is_user_admin/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ({"api_key": "123"}, 403),
            ({"telegram_id": 0}, 403),
            ({"api_key": "123", "grade": 0}, 403),
            ({"api_key": settings.API_KEY}, 400),
            (
                {
                    "api_key": settings.API_KEY,
                    "grade": 11,
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "letter": "Б",
                },
                400,
            ),
            (
                {
                    "api_key": settings.API_KEY,
                    "grade": 11,
                    "letter": "Б",
                },
                200,
            ),
        ],
    )
    def test_et_user_eng_teachers(self, data, status_code):
        response = client.post(
            "/api/v1/get_user_eng_teachers/",
            data=data,
            format="json",
        )
        self.assertEquals(response.status_code, status_code)
