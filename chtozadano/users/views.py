from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView

from users.models import SignIn


class SignInView(APIView):
    def post(self, request):
        if request.data["api_key"] != settings.API_KEY:
            return HttpResponse("Uncorrect api key")
        telegram_id = request.data["telegram_id"]
        confirmation_code = request.data["confirmation_code"]
        user_name = request.data["name"]
        SignIn.objects.create(
            telegram_id=telegram_id,
            confirmation_code=confirmation_code,
            name=user_name,
        )
        return HttpResponse(
            f"Информация о пользователе {telegram_id}"
            f" успешно внесена в таблицу SignIN",
        )

    def get(self, request):
        objects = SignIn.objects.all()
        return HttpResponse(str(objects))
