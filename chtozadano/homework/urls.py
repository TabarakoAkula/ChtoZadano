from django.urls import path

from homework.views import ChooseGrLePage, HomeworkPage

app_name = "homework"

urlpatterns = [
    path("", HomeworkPage.as_view(), name="homework_page"),
    path("choose_class/", ChooseGrLePage.as_view(), name="choose_grad_let"),
]
