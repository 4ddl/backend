from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.views import Response

from ddl.settings import PAGE_CACHE_AGE
# Create your views here.
from problem.models import Problem
from problem.serializers import ProblemSerializer, ProblemListSerializer
from utils.permissions import check_permissions
from utils.response import msg


class ProblemViewSet(viewsets.GenericViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @check_permissions('problem.add_problem')
    def create(self, request):
        serializer = ProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('Successful create.'))

    @check_permissions('problem.change_problem')
    def update(self, request, *args, **kwargs):
        problem = self.get_object()
        serializer = ProblemSerializer(problem, data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('Successful update.'))

    @check_permissions('problem.delete_problem')
    def destroy(self, request, *args, **kwargs):
        problem = self.get_object()
        problem.delete()
        return Response(msg('Successful delete.'))

    @method_decorator(cache_page(PAGE_CACHE_AGE, cache='page'))
    def retrieve(self, request, *args, **kwargs):
        problem = self.get_object()
        serializer = ProblemSerializer(problem)
        return Response(msg(serializer.data))

    def get_serializer_class(self):
        if self.action == 'list':
            return ProblemListSerializer
        else:
            return self.serializer_class
