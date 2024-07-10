from django.urls import path

from users.views import (
    AccountPage,
    BecomeAdminAccept,
    BecomeAdminDecline,
    BecomeAdminPage,
    ChangeContactsPage,
    Logout,
    ShowBecomeAdmin,
    SignInPage,
    SignInPasswordPage,
    SignUpPage,
    SignUpPasswordPage,
)


app_name = "users"

urlpatterns = [
    path("sign_in/", SignInPage.as_view(), name="signin_page"),
    path("sign_up/", SignUpPage.as_view(), name="signup_page"),
    path(
        "sign_in_password/",
        SignInPasswordPage.as_view(),
        name="signin_password_page",
    ),
    path(
        "sign_up_password/",
        SignUpPasswordPage.as_view(),
        name="signup_password_page",
    ),
    path("account/", AccountPage.as_view(), name="account_page"),
    path("logout/", Logout.as_view(), name="logout"),
    path("become_admin/", BecomeAdminPage.as_view(), name="become_admin"),
    path(
        "show_become_admin/",
        ShowBecomeAdmin.as_view(),
        name="show_become_admin",
    ),
    path(
        "show_become_accept/<int:telegram_id>",
        BecomeAdminAccept.as_view(),
        name="accept_become_admin",
    ),
    path(
        "show_become_decline/<int:telegram_id>",
        BecomeAdminDecline.as_view(),
        name="decline_become_admin",
    ),
    path(
        "change_contacts/",
        ChangeContactsPage.as_view(),
        name="change_contacts",
    ),
]
