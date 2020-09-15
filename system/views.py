from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ddl.settings import LANGUAGE_COOKIE_NAME, LANGUAGES
from utils.response import msg
from .serializers import LanguageSerializer
from rest_framework.permissions import IsAdminUser
from user.models import User
from problem.models import Problem
from submission.models import Submission


class SystemViewSet(viewsets.GenericViewSet):

    # 获取API接口支持的语言和修改API接口的语言
    @action(methods=['GET', 'POST'], detail=False)
    def language(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            res = Response(msg(_('Success.')))
            res.set_cookie(LANGUAGE_COOKIE_NAME, serializer.validated_data['language'])
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
