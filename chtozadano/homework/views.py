import json

from django.shortcuts import redirect, render
from django.views import View

from homework.forms import ChooseGradLetForm
from homework.models import Homework


class HomeworkPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            grade = request.user.server_user.grade
            letter = request.user.server_user.letter
        else:
            try:
                data = json.loads(request.COOKIES.get("hw_data"))
            except TypeError:
                return redirect("homework:choose_grad_let")
            grade = data["grade"]
            letter = data["letter"]
            if not grade or not letter:
                return redirect("homework:choose_grad_let")
        data = Homework.objects.filter(grade=grade, letter=letter).all()
        return render(
            request,
            "homework/homework.html",
            context={
                "homework": data,
            },
        )


class ChooseGrLePage(View):
    def get(self, request):
        grade = request.COOKIES.get("grade")
        letter = request.COOKIES.get("letter")
        return render(
            request,
            "homework/choose_grad_let.html",
            context={
                "grade": grade,
                "letter": letter,
                "form": ChooseGradLetForm,
            },
        )

    def post(self, request):
        data = {
            "grade": request.POST.get("grade"),
            "letter": request.POST.get("letter"),
        }
        response = redirect("homework:homework_page")
        response.set_cookie("hw_data", json.dumps(data))
        return response
