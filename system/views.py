from rest_framework import viewsets
from .serializers import LanguageSerializer
from rest_framework.response import Response
from utils.response import msg
from django.utils.translation import gettext as _
from ddl.settings import LANGUAGE_COOKIE_NAME, LANGUAGES
from rest_framework.decorators import action


class SystemViewSet(viewsets.GenericViewSet):
    serializer_class = LanguageSerializer

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
