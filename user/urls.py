from django.urls import path

from user.views import AuthAPI

urlpatterns = [
    path('auth', AuthAPI.as_view())
]
