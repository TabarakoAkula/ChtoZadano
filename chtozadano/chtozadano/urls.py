import chtozadano.views
from django.conf import settings
import django.conf.global_settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

import homework.views
import users.urls

app_name = "chtozadano"

urlpatterns = [
    path(
        "api/v1/code_confirmation/",
        csrf_exempt(users.views.CodeConfirmationApi.as_view()),
    ),
    path(
        "api/v1/get_last_homework/",
        csrf_exempt(homework.views.GetLastHomeworkAPI.as_view()),
    ),
    path(
        "api/v1/get_homework_for_subject/",
        csrf_exempt(homework.views.GetOneSubjectAPI.as_view()),
    ),
    path(
        "api/v1/become_admin/",
        csrf_exempt(users.views.BecomeAdminAPI.as_view()),
    ),
    path(
        "api/v1/become_admin_accept_decline/",
        csrf_exempt(users.views.AcceptDeclineBecomeAdminAPI.as_view()),
    ),
    path("mainpage/", chtozadano.views.MainPage.as_view(), name="mainpage"),
    path("admin/", admin.site.urls),
    path("user/", include("users.urls")),
    path("homework/", include("homework.urls")),
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {"document_root": settings.STATIC_ROOT},
    ),
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(
    django.conf.settings.MEDIA_URL,
    document_root=django.conf.settings.MEDIA_ROOT,
)

if django.conf.settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
