from django.urls import path

from users.views import (
    AccountPage,
    Logout,
    SignInPage,
    SignUpPage,
)


app_name = "users"

urlpatterns = [
    path("sign_in/", SignInPage.as_view(), name="signin_page"),
    path("sign_up/", SignUpPage.as_view(), name="signup_page"),
    path("account/", AccountPage.as_view(), name="account_page"),
    path("logout/", Logout.as_view(), name="logout"),
]
