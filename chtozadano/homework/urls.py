from django.urls import path

from homework.views import (
    AddHomeworkPage,
    AddMailingPage,
    AllHomeworkPage,
    ChooseGrLePage,
    DeleteHomework,
    DeleteMailing,
    EditHomework,
    EditHomeworkData,
    EditMailingPage,
    HomeworkPage,
)

app_name = "homework"

urlpatterns = [
    path("", HomeworkPage.as_view(), name="homework_page"),
    path("all/", AllHomeworkPage.as_view(), name="all_homework_page"),
    path("choose_class/", ChooseGrLePage.as_view(), name="choose_grad_let"),
    path("add/", AddHomeworkPage.as_view(), name="add_homework_page"),
    path("add_mailing/", AddMailingPage.as_view(), name="add_mailing_page"),
    path(
        "delete/<int:homework_id>/",
        DeleteHomework.as_view(),
        name="delete_homework",
    ),
    path(
        "delete_mailing/<int:homework_id>/",
        DeleteMailing.as_view(),
        name="delete_mailing",
    ),
    path(
        "edit/<int:homework_id>/",
        EditHomework.as_view(),
        name="edit_homework",
    ),
    path(
        "edit/<int:homework_id>/<str:r_type>/<int:file_id>",
        EditHomeworkData.as_view(),
        name="edit_files_homework",
    ),
    path(
        "edit_mailing/<int:homework_id>/",
        EditMailingPage.as_view(),
        name="edit_mailing",
    ),
]
