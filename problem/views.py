from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# Create your views here.
from problem.models import Problem
from problem.serializers import ProblemSerializer
from rest_framework.views import Response
from utils.response import msg
from ddl.settings import PAGE_CACHE_AGE
from django.core.exceptions import ObjectDoesNotExist
from utils.permissions import check_permissions


class ProblemViewSet(viewsets.ViewSet):

    @check_permissions('problem.add_problem')
    def create(self, request):
        serializer = ProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('Successful create.'))

    @check_permissions('problem.change_problem')
    def update(self, request, pk=None):
        try:
            problem = Problem.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(msg(err='Object not exist.'))
        serializer = ProblemSerializer(problem, data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('Successful update.'))

    @check_permissions('problem.delete_problem')
    def destroy(self, request, pk=None):
        try:
            problem = Problem.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(msg(err='Object not exist.'))
        problem.delete()
        return Response(msg('Successful delete.'))

    def list(self, request, *args, **kwargs):
        queryset = Problem.objects.all()
        serializer = ProblemSerializer(queryset, many=True)
        return Response(msg(serializer.data))

    @method_decorator(cache_page(PAGE_CACHE_AGE, cache='page'))
    def retrieve(self, request, pk=None):
        try:
            problem = Problem.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(msg(err='Object not exist.'))
        serializer = ProblemSerializer(problem)
        return Response(msg(serializer.data))
