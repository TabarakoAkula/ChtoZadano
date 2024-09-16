import json
import os

from django.http import HttpResponse
from django.shortcuts import render

from users.models import User


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.split("/")[1]
        try:
            if path == "api":
                if request.method == "POST":
                    request_body = request.body.decode("utf-8")
                    json_body = json.loads(request_body)
                    try:
                        if json_body["api_key"] != os.getenv("API_KEY"):
                            return HttpResponse("Invalid api key", status=403)
                    except KeyError:
                        return HttpResponse("Empty api key", status=403)
        except (json.decoder.JSONDecodeError, TypeError):
            return HttpResponse("Bad request data", status=400)
        return self.get_response(request)


class SiteTechnicalWorksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.split("/")[1]
        if path not in ["api", "admin"] and not request.user.is_superuser:
            return render(
                request,
                "technical_works.html",
                context={
                    "messages": ("Пожалуйста, дождитесь окончания работ ❤️",),
                },
            )
        return self.get_response(request)


class APITechnicalWorksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.split("/")[1]
        if path == "api":
            request_body = request.body.decode("utf-8")
            json_body = json.loads(request_body)
            user_obj = User.objects.filter(
                telegram_id=json_body["telegram_id"],
            ).all()
            if not user_obj or not user_obj[0].user.is_superuser:
                return HttpResponse("API now not available", status=503)
        return self.get_response(request)
