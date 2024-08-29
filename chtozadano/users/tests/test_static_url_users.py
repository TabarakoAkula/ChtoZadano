from http import HTTPStatus

from django.contrib.auth.models import User as DjangoUser
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized


class StaticUrlTests(TestCase):
    multi_db = True
    fixtures = ["fixtures/test_static_url_data.json"]

    @parameterized.expand(
        [
            "",
            "test_user",
            "test_admin",
            "test_superuser",
        ],
    )
    def test_index_endpoint(self, username):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("index"))
        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    @parameterized.expand(
        [
            "",
            "test_user",
            "test_admin",
            "test_superuser",
        ],
    )
    def test_mainpage_endpoint(self, username):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("mainpage"))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    @parameterized.expand(
        [
            ("", 200),
            ("test_user", 302),
            ("test_admin", 302),
            ("test_superuser", 302),
        ],
    )
    def test_signin_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:signin_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 200),
            ("test_user", 302),
            ("test_admin", 302),
            ("test_superuser", 302),
        ],
    )
    def test_signup_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:signup_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 200),
            ("test_user", 302),
            ("test_admin", 302),
            ("test_superuser", 302),
        ],
    )
    def test_signin_password_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:signin_password_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 200),
            ("test_user", 302),
            ("test_admin", 302),
            ("test_superuser", 302),
        ],
    )
    def test_signup_password_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:signup_password_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 200),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_account_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:account_page"))
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", "/user/sign_in/"),
            ("test_user", "/mainpage/"),
            ("test_admin", "/mainpage/"),
            ("test_superuser", "/mainpage/"),
        ],
    )
    def test_logout_endpoint(self, username, location):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:logout"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response["Location"], location)

    @parameterized.expand(
        [
            ("", "/user/sign_in/", 302),
            ("test_user", "", 200),
            ("test_admin", "/homework/", 302),
            ("test_superuser", "/homework/", 302),
        ],
    )
    def test_become_admin_endpoint(self, username, location, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:become_admin"))
        if status_code == 302:
            self.assertEquals(response["Location"], location)
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", "/user/account/", 302),
            ("test_user", "/user/account/", 302),
            ("test_admin", "/user/account/", 302),
            ("test_admin_becomeadminaccept", "/user/account/", 302),
        ],
    )
    def test_show_become_admin_accept_endpoint(
        self,
        username,
        location,
        status_code,
    ):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(
            reverse("users:accept_become_admin", kwargs={"telegram_id": 4}),
        )
        if status_code == 302:
            self.assertEquals(response["Location"], location)
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", "/user/account/", 302),
            ("test_user", "/user/account/", 302),
            ("test_admin", "/user/account/", 302),
            ("test_admin_becomeadmin", "/user/account/", 302),
        ],
    )
    def test_show_become_admin_decline_endpoint(
        self,
        username,
        location,
        status_code,
    ):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(
            reverse("users:decline_become_admin", kwargs={"telegram_id": 4}),
        )
        if status_code == 302:
            self.assertEquals(response["Location"], location)
        self.assertEquals(response.status_code, status_code)

    @parameterized.expand(
        [
            ("", 302),
            ("test_user", 200),
            ("test_admin", 200),
            ("test_superuser", 200),
        ],
    )
    def test_change_contacts_endpoint(self, username, status_code):
        if username:
            self.client.force_login(
                DjangoUser.objects.get_or_create(username=username)[0],
            )
        response = self.client.get(reverse("users:change_contacts"))
        self.assertEquals(response.status_code, status_code)
