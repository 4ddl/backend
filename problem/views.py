from rest_framework import viewsets

# Create your views here.
from problem.models import Problem
from problem.serializers import ProblemSerializer
from rest_framework.views import Response
from user import Perms
from user.permissions import IfAdminOrReadOnly
from utils import msg
from django.shortcuts import get_object_or_404


class ProblemViewSet(viewsets.ViewSet):
    perms = [Perms.PROBLEM_CREATE]
    permission_classes = [IfAdminOrReadOnly]

    @staticmethod
    def create(request):
        serializer = ProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('successful create'))

    @staticmethod
    def update(request, pk=None):
        queryset = Problem.objects.all()
        problem = get_object_or_404(queryset, pk=pk)
        serializer = ProblemSerializer(problem, data=request.data)
        if serializer.is_valid():
            serializer.author = request.user
            serializer.save()
        return Response(msg('successful update'))

    @staticmethod
    def destroy(request, pk=None):
        queryset = Problem.objects.all()
        problem = get_object_or_404(queryset, pk=pk)
        problem.delete()
        return Response(msg('successful delete'))

    @staticmethod
    def list(request, *args, **kwargs):
        queryset = Problem.objects.all()
        serializer = ProblemSerializer(queryset, many=True)
        return Response(msg(serializer.data))

    @staticmethod
    def retrieve(request, pk=None):
        queryset = Problem.objects.all()
        problem = get_object_or_404(queryset, pk=pk)
        serializer = ProblemSerializer(problem)
        return Response(msg(serializer.data))
