from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from django.utils.translation import gettext as _
from utils.permissions import is_authenticated
from utils.response import msg
from .models import Submission
from .serializers import SubmissionSerializer, SubmissionShortSerializer, SubmissionCreateSerializer
from django.utils import timezone
from datetime import timedelta
from django_filters import rest_framework as filters


class SubmissionFilter(filters.FilterSet):
    verdict = filters.CharFilter(field_name='verdict', lookup_expr='iexact')
    user = filters.CharFilter(field_name='user', lookup_expr='exact')

    class Meta:
        model = Submission
        fields = ['verdict', 'user']


class SubmissionViewSet(viewsets.GenericViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    filterset_class = SubmissionFilter

    @is_authenticated()
    def create(self, request: Request):
        last_submit_time = request.user.last_submit_time
        if last_submit_time is not None and timezone.now() < last_submit_time + timedelta(seconds=10):
            return Response(msg(err=_('Can\'t submit twice within 10 seconds.')))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(user=request.user)
        return Response(msg(SubmissionShortSerializer(submission).data))

    def list(self, request: Request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        submission = get_object_or_404(queryset, pk=pk)
        serializer = SubmissionShortSerializer(submission)
        return Response(msg(serializer.data))

    @action(detail=True, methods=['get'])
    def personal(self, request, pk=None):
        queryset = self.get_queryset()
        submission = get_object_or_404(queryset, pk=pk)
        if submission.user == request.user or request.user.is_staff:
            serializer = SubmissionSerializer(submission)
            return Response(msg(serializer.data))
        raise PermissionDenied

    def get_serializer_class(self):
        if self.action == 'list':
            return SubmissionShortSerializer
        elif self.action == 'create':
            return SubmissionCreateSerializer
        else:
            return self.get_serializer_class()
