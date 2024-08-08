import json
import os

from django.http import HttpResponse
from django.shortcuts import render


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.split("/")[1]
        if path == "api":
            if request.method == "POST":
                request_body = request.body.decode("utf-8")
                json_body = json.loads(request_body)
                try:
                    if json_body["api_key"] != os.getenv("API_KEY"):
                        return HttpResponse("Invalid api key", status=403)
                except KeyError:
                    return HttpResponse("Empty api key", status=403)
        return self.get_response(request)


class SiteTechnicalWorksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.split("/")[1]
        if path != "api":
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
            return HttpResponse("API now not available", status=503)
        return self.get_response(request)
