from django.urls import path

from user.views import AuthAPI,CaptchaAPI

urlpatterns = [
    path('auth', AuthAPI.as_view()),
    path('captcha', CaptchaAPI.as_view())
]
