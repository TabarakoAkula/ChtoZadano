from django.urls import path

import homework.api.views
import users.api.views

urlpatterns = [
    path(
        "code_confirmation/",
        users.api.views.CodeConfirmationAPI.as_view(),
    ),
    path(
        "create_user/",
        users.api.views.CreateUserAPI.as_view(),
    ),
    path(
        "get_contacts/",
        users.api.views.GetContactsAPI.as_view({"post": "get_contacts"}),
    ),
    path(
        "change_contacts/",
        users.api.views.ChangeContactsAPI.as_view(),
    ),
    path(
        "get_quotes_status/",
        users.api.views.GetQuotesAPI.as_view(),
    ),
    path(
        "change_quotes/",
        users.api.views.ChangeQuotesAPI.as_view(),
    ),
    path(
        "change_grade_letter/",
        users.api.views.ChangeGradeLetterAPI.as_view(),
    ),
    path(
        "get_chat_mode/",
        users.api.views.GetChatModeAPI.as_view(),
    ),
    path(
        "change_chat_mode/",
        users.api.views.ChangeChatModeAPI.as_view(),
    ),
    path(
        "show_become_admin/",
        users.api.views.ShowBecomeAdminAPI.as_view(),
    ),
    path(
        "become_admin/",
        users.api.views.BecomeAdminAPI.as_view(),
    ),
    path(
        "become_admin_accept_decline/",
        users.api.views.AcceptDeclineBecomeAdminAPI.as_view(),
    ),
    path(
        "become_admin_delete_user/",
        users.api.views.DeleteUserBecomeAdminAPI.as_view(),
    ),
    path(
        "is_user_in_system/",
        users.api.views.IsUserInSystemAPI.as_view(),
    ),
    path(
        "get_admins/",
        users.api.views.GetAdminsAPI.as_view({"post": "get_admins"}),
    ),
    path(
        "is_user_admin/",
        users.api.views.IsUserAdminAPI.as_view(),
    ),
    path(
        "get_last_homework_all_subjects/",
        homework.api.views.GetLastHomeworkAllSubjectsAPI.as_view(
            {"post": "get_homework"},
        ),
    ),
    path(
        "get_homework_for_subject/",
        homework.api.views.GetOneSubjectAPI.as_view({"post": "get_homework"}),
    ),
    path(
        "get_homework_from_date/",
        homework.api.views.GetAllHomeworkFromDateAPI.as_view(
            {"post": "get_homework"},
        ),
    ),
    path(
        "get_homework_from_id/",
        homework.api.views.GetHomeworkFromIdAPI.as_view(
            {"post": "get_homework"},
        ),
    ),
    path(
        "get_tomorrow_homework/",
        homework.api.views.GetTomorrowHomeworkAPI.as_view(
            {"post": "get_homework"},
        ),
    ),
    path(
        "add_homework/",
        homework.api.views.AddHomeWorkAPI.as_view(),
    ),
    path(
        "edit_homework_description/",
        homework.api.views.EditHomeworkDescriptionAPI.as_view(),
    ),
    path(
        "edit_homework_images/",
        homework.api.views.EditHomeworkImagesAPI.as_view(),
    ),
    path(
        "edit_homework_files/",
        homework.api.views.EditHomeworkFilesAPI.as_view(),
    ),
    path(
        "delete_homework/",
        homework.api.views.DeleteHomeworkAPI.as_view(),
    ),
    path(
        "get_mailing/",
        homework.api.views.GetMailingAPI.as_view({"post": "get_mailing"}),
    ),
    path(
        "add_mailing/",
        homework.api.views.AddMailingAPI.as_view(),
    ),
    path(
        "edit_mailing/",
        homework.api.views.EditMailingAPI.as_view(),
    ),
    path(
        "edit_mailing_description/",
        homework.api.views.EditMailingDescriptionAPI.as_view(),
    ),
    path(
        "edit_mailing_images/",
        homework.api.views.EditMailingImagesAPI.as_view(),
    ),
    path(
        "edit_mailing_files/",
        homework.api.views.EditMailingFilesAPI.as_view(),
    ),
    path(
        "delete_mailing/",
        homework.api.views.DeleteMailingAPI.as_view(),
    ),
    path(
        "change_todo/",
        homework.api.views.TodoWorkAPI.as_view(),
    ),
    path(
        "get_tomorrow_schedule/",
        homework.api.views.GetTomorrowScheduleAPI.as_view(
            {"post": "get_schedule"},
        ),
    ),
    path(
        "delete_old_homework/",
        homework.api.views.DeleteOldHomeworkAPI.as_view(),
    ),
    path(
        "add_schedule/",
        homework.api.views.AddScheduleAPI.as_view(),
    ),
    path(
        "get_week_schedule/",
        homework.api.views.GetWeekScheduleAPI.as_view(
            {"post": "get_schedule"},
        ),
    ),
]
