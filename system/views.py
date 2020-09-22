from celery.bin.control import inspect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from oj.celery import app as celery_app
from oj.settings import LANGUAGE_COOKIE_NAME, LANGUAGES, PAGE_CACHE_AGE
from problem.models import Problem
from submission.models import Submission
from user.models import User
from utils.response import msg
from .serializers import LanguageSerializer


class SystemViewSet(viewsets.GenericViewSet):
    @method_decorator(cache_page(PAGE_CACHE_AGE))
    @action(methods=['GET'], detail=False)
    def queue(self, request, *args, **kwargs):
        try:
            inspect_task = inspect(app=celery_app)
            replies = inspect_task.run('active_queues')
            res = [{
                'name': key,
                'queue': [item['name'] for item in replies[key]]
            } for key in replies.keys()]
            return Response(msg(data=res))
        except Exception as e:
            return Response(msg(err=str(e)))

    # 获取API接口支持的语言和修改API接口的语言
    @action(methods=['GET', 'POST'], detail=False)
    def language(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            res = Response(msg(_('Success.')))
            res.set_cookie(key=LANGUAGE_COOKIE_NAME, value=serializer.validated_data['language'], samesite='lax')
            return res
        else:
            return Response(msg(LANGUAGES))

    @action(methods=['GET'], detail=False, permission_classes=[IsAdminUser])
    def info(self, request, *args, **kwargs):
        user_cnt = User.objects.all().count()
        problem_cnt = Problem.objects.all().count()
        submission_cnt = Submission.objects.all().count()
        return Response(msg({
            'user_cnt': user_cnt,
            'problem_cnt': problem_cnt,
            'submission_cnt': submission_cnt
        }))

    def get_serializer_class(self):
        if self.action == 'language':
            return LanguageSerializer
        return self.serializer_class
