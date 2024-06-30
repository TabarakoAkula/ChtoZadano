from django.shortcuts import render
from django.views import View


class MainPage(View):
    def get(self, request):
        return render(request, "mainpage.html")
