from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils import msg

from .models import Submission
from .serializers import SubmissionSerializer


class SubmissionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def create(request: Request):
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(msg('successful create'))

    @staticmethod
    def list(request: Request):
        queryset = Submission.objects.all()
        serializer = SubmissionSerializer(queryset, many=True)
        return Response(msg(serializer.data))

    @staticmethod
    def retrieve(request, pk=None):
        queryset = Submission.objects.all()
        submission = get_object_or_404(queryset, pk=pk)
        serializer = SubmissionSerializer(submission)
        return Response(msg(serializer.data))
