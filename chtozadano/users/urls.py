from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from users.views import SignInView

urlpatterns = [
    path("sign_in/", csrf_exempt(SignInView.as_view())),
]
