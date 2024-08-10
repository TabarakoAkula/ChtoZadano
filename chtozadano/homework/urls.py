from django.urls import path

import homework.views

app_name = "homework"

urlpatterns = [
    path("", homework.views.HomeworkPage.as_view(), name="homework_page"),
    path(
        "all/",
        homework.views.AllHomeworkPage.as_view(),
        name="all_homework_page",
    ),
    path(
        "weekday/<int:weekday>/",
        homework.views.WeekdayHomeworkPage.as_view(),
        name="weekday_homework",
    ),
    path(
        "choose_class/",
        homework.views.ChooseGrLePage.as_view(),
        name="choose_grad_let",
    ),
    path(
        "add/",
        homework.views.AddHomeworkPage.as_view(),
        name="add_homework_page",
    ),
    path(
        "edit/<int:homework_id>/",
        homework.views.EditHomework.as_view(),
        name="edit_homework",
    ),
    path(
        "edit/<int:homework_id>/<str:r_type>/<int:file_id>",
        homework.views.EditHomeworkData.as_view(),
        name="edit_files_homework",
    ),
    path(
        "delete/<int:homework_id>/",
        homework.views.DeleteHomework.as_view(),
        name="delete_homework",
    ),
    path(
        "add_mailing/",
        homework.views.AddMailingPage.as_view(),
        name="add_mailing_page",
    ),
    path(
        "edit_mailing/<int:homework_id>/",
        homework.views.EditMailingPage.as_view(),
        name="edit_mailing",
    ),
    path(
        "delete_mailing/<int:homework_id>/",
        homework.views.DeleteMailing.as_view(),
        name="delete_mailing",
    ),
    path(
        "mark_done/<int:homework_id>",
        homework.views.MarkDone.as_view(),
        name="mark_done",
    ),
    path("schedule/", homework.views.SchedulePage.as_view(), name="schedule"),
]
