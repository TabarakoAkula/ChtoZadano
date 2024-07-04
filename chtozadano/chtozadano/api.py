from django.urls import path

import homework.views
import users.views

urlpatterns = [
    path(
        "code_confirmation/",
        users.views.CodeConfirmationApi.as_view(),
    ),
    path(
        "get_last_homework/",
        homework.views.GetLastHomeworkAPI.as_view(),
    ),
    path(
        "get_homework_for_subject/",
        homework.views.GetOneSubjectAPI.as_view(),
    ),
    path(
        "become_admin/",
        users.views.BecomeAdminAPI.as_view(),
    ),
    path(
        "become_admin_accept_decline/",
        users.views.AcceptDeclineBecomeAdminAPI.as_view(),
    ),
    path(
        "change_grade_letter/",
        users.views.ChangeGradeLetterAPI.as_view(),
    ),
    path(
        "change_chat_mode/",
        users.views.ChangeChatModeAPI.as_view(),
    ),
    path(
        "get_homework_from_date/",
        homework.views.GetAllHomeworkFromDateAPI.as_view(),
    ),
    path(
        "delete_homework/",
        homework.views.DeleteHomeworkAPI.as_view(),
    ),
    path(
        "add_homework/",
        homework.views.AddHomeWorkAPI.as_view(),
    ),
    path(
        "edit_homework/",
        homework.views.EditHomeworkAPI.as_view(),
    ),
    path(
        "edit_homework_description/",
        homework.views.EditHomeworkDescriptionAPI.as_view(),
    ),
    path(
        "edit_homework_images/",
        homework.views.EditHomeworkImagesAPI.as_view(),
    ),
    path(
        "edit_homework_files/",
        homework.views.EditHomeworkFilesAPI.as_view(),
    ),
    path(
        "get_homework_from_id/",
        homework.views.AddHomeWorkAPI.as_view(),
    ),
]
