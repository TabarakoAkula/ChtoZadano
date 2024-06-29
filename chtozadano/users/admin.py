from django.contrib import admin

from users.models import SignIn, Todo, User

admin.site.register(User)
admin.site.register(SignIn)
admin.site.register(Todo)
