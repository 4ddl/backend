from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# Create your views here.
from problem.models import Problem
from problem.serializers import ProblemSerializer
from rest_framework.views import Response
from user import Perms
from user.permissions import IfAdminOrReadOnly
from utils import msg
from django.shortcuts import get_object_or_404
from ddl.settings import PAGE_CACHE_AGE
from django.core.exceptions import ObjectDoesNotExist


class ProblemViewSet(viewsets.ViewSet):
    perms = [Perms.PROBLEM_CREATE]
    permission_classes = [IfAdminOrReadOnly]

    @staticmethod
    def create(request):
        serializer = ProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('Successful create.'))

    @staticmethod
    def update(request, pk=None):
        queryset = Problem.objects.all()
        problem = get_object_or_404(queryset, pk=pk)
        serializer = ProblemSerializer(problem, data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('Successful update.'))

    @staticmethod
    def destroy(request, pk=None):
        try:
            problem = Problem.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(msg(err='Object not exist.'))
        problem.delete()
        return Response(msg('Successful delete.'))

    @staticmethod
    def list(request, *args, **kwargs):
        queryset = Problem.objects.all()
        serializer = ProblemSerializer(queryset, many=True)
        return Response(msg(serializer.data))

    @staticmethod
    @method_decorator(cache_page(PAGE_CACHE_AGE, cache='page'))
    def retrieve(request, pk=None):
        try:
            problem = Problem.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(msg(err='Object not exist.'))
        serializer = ProblemSerializer(problem)
        return Response(msg(serializer.data))
