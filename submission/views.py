from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from utils.permissions import is_authenticated
from utils.response import msg
from .models import Submission
from .serializers import SubmissionSerializer, SubmissionShortSerializer


class SubmissionViewSet(viewsets.ViewSet):
    @is_authenticated()
    def create(self, request: Request):
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(msg('successful create'))

    def list(self, request: Request):
        queryset = Submission.objects.all()
        serializer = SubmissionShortSerializer(queryset, many=True)
        return Response(msg(serializer.data))

    def retrieve(self, request, pk=None):
        queryset = Submission.objects.all()
        submission = get_object_or_404(queryset, pk=pk)
        if submission.user == request.user or request.user.is_staff:
            serializer = SubmissionSerializer(submission)
            return Response(msg(serializer.data))
        raise PermissionDenied
