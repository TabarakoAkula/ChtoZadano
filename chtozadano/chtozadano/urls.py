import chtozadano.views
from django.conf import settings
import django.conf.global_settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve

app_name = "chtozadano"

urlpatterns = [
    path("", chtozadano.views.RedirectToMainPage.as_view()),
    path("api/v1/", include("chtozadano.api")),
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
