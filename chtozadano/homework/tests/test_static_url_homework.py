from django.contrib.auth.models import User as DjangoUser
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized


class StaticUrlTests(TestCase):
    multi_db = True
    fixtures = ["fixtures/test_static_url_data.json"]

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 200),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_homework_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("homework:homework_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 200),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_all_homework_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("homework:all_homework_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302, 1),
            ("test_user", 200, 1),
            ("test_admin", 200, 1),
            ("test_superuser", 200, 1),
            ("test_user", 302, 0),
        ],
    )
    def test_weekday_homework_endpoint(self, username, status_code, weekday):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(
            reverse("homework:weekday_homework", kwargs={"weekday": weekday}),
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 200),
            ("test_user", 200),
            ("test_admin", 302),
            ("test_superuser", 200),
        ],
    )
    def test_choose_grade_letter_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("homework:choose_grad_let"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 302),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_add_homework_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("homework:add_homework_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 302),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_add_mailing_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("homework:add_mailing_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 302),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_delete_homework_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(
            reverse("homework:delete_homework", kwargs={"homework_id": 1}),
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302, [2, 3, 4]),
            ("test_user", 302, [2, 3, 4]),
            ("test_admin", 200, [2]),
            ("test_superuser", 200, [2, 3, 4]),
        ],
    )
    def test_delete_mailing_endpoint(self, username, status_code, homeworks):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        for i in homeworks:
            response = self.client.get(
                reverse("homework:delete_mailing", kwargs={"homework_id": i}),
            )
            self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 302),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_edit_homework_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(
            reverse("homework:edit_homework", kwargs={"homework_id": 1}),
        )
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302, "/homework/"),
            ("test_user", 302, "/homework/"),
            ("test_admin", 302, "/homework/edit/1/"),
            ("test_superuser", 302, "/homework/edit/1/"),
        ],
    )
    def test_edit_homework_files_endpoint(
        self,
        username,
        status_code,
        location,
    ):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        for i in ["img", "file"]:
            response = self.client.get(
                reverse(
                    "homework:edit_files_homework",
                    kwargs={"homework_id": 1, "r_type": i, "file_id": 1},
                ),
            )
        self.assertEquals(response.status_code, status_code)
        self.assertEquals(response["Location"], location)

    @parameterized.expand(
        [
            ("", 302, [2, 3, 4]),
            ("test_user", 302, [2, 3, 4]),
            ("test_admin", 200, [2]),
            ("test_superuser", 200, [2, 3, 4]),
        ],
    )
    def test_edit_mailing_endpoint(self, username, status_code, homeworks):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        for i in homeworks:
            response = self.client.get(
                reverse(
                    "homework:edit_mailing",
                    kwargs={"homework_id": i},
                ),
            )
            self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302, "/user/sign_in/"),
            ("test_user", 302, "/homework/#1"),
            ("test_admin", 302, "/homework/#1"),
            ("test_superuser", 302, "/homework/#1"),
        ],
    )
    def test_mark_done_endpoint(self, username, status_code, location):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(
            reverse("homework:mark_done", kwargs={"homework_id": 1}),
        )
        self.assertEquals(response.status_code, status_code)
        self.assertEquals(response["Location"], location)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 200),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_schedule_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("homework:schedule"))
        self.assertEquals(response.status_code, status_code)
