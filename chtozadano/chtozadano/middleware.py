import json
import os

from django.http import HttpResponse


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.split("/")[1]
        if path == "api":
            if request.method == "POST":
                request_body = request.body.decode("utf-8")
                json_body = json.loads(request_body)
                if json_body["api_key"] != os.getenv("API_KEY"):
                    return HttpResponse("Invalid api key")
        return self.get_response(request)
