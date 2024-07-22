from django.shortcuts import redirect, render
from django.views import View


class MainPage(View):
    def get(self, request):
        return render(request, "mainpage.html")


class RedirectToMainPage(View):
    def get(self, request):
        return redirect("mainpage")
