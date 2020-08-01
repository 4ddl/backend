from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils import msg

from .models import Submission
from .serializers import SubmissionSerializers


class SubmissionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def create(request: Request):
        serializer = SubmissionSerializers(request.data)
        if serializer.is_valid():
            serializer.user = request.user
            serializer.save()
            return Response(msg('successful create'))
        return Response(msg(err='form invalid'))

    @staticmethod
    def list(request: Request):
        queryset = Submission.objects.all()
        serializer = SubmissionSerializers(queryset, many=True)
        return Response(msg(serializer.data))

    @staticmethod
    def retrieve(request, pk=None):
        queryset = Submission.objects.all()
        submission = get_object_or_404(queryset, pk=pk)
        serializer = SubmissionSerializers(submission)
        return Response(msg(serializer.data))
