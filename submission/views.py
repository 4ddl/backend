from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.response import msg

from .models import Submission
from .serializers import SubmissionSerializer, SubmissionShortSerializer


class SubmissionViewSet(viewsets.ViewSet):
    permission_classes_action = {
        'create': [IsAuthenticated]
    }

    @staticmethod
    def create(request: Request):
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(msg('successful create'))

    @staticmethod
    def list(request: Request):
        queryset = Submission.objects.all()
        serializer = SubmissionShortSerializer(queryset, many=True)
        return Response(msg(serializer.data))

    @staticmethod
    def retrieve(request, pk=None):
        queryset = Submission.objects.all()
        submission = get_object_or_404(queryset, pk=pk)
        if submission.user == request.user or request.user.is_admin:
            serializer = SubmissionSerializer(submission)
            return Response(msg(serializer.data))
        return Response(msg(err='Permission denied'))

    def get_permissions(self):
        return [p() for p in self.permission_classes_action[self.action]] \
            if self.action in self.permission_classes_action \
            else [AllowAny()]
