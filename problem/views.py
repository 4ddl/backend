import os
from uuid import uuid4

from PIL import Image
from django.db.models import Q
from django.http.response import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.views import Response

from ddl.settings import PROBLEM_IMAGE_DIR
from problem.forms import ImageNameForms, UploadImageForms
# Create your views here.
from problem.models import Problem
from problem.serializers import ProblemSerializer, ProblemListSerializer
from utils.permissions import check_permissions
from utils.response import msg


class ProblemFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name='id', lookup_expr='icontains')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Problem
        fields = ['id', 'title']


class ProblemViewSet(viewsets.GenericViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filterset_class = ProblemFilter

    def list(self, request, *args, **kwargs):
        """
        管理员的话，返回所有题目列表
        普通登录的话，返回可以查看的，或者自己上传的题目列表
        未登录的话，仅返回可以查看的题目列表
        :param request: Request
        :param args:
        :param kwargs:
        :return: Response
        """
        if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
        elif request.user.is_authenticated:
            queryset = self.filter_queryset(self.get_queryset().filter(
                Q(public=Problem.VIEW_ONLY) | Q(public=Problem.VIEW_SUBMIT) | Q(author=request.user)))
        else:
            queryset = self.filter_queryset(self.get_queryset().filter(
                Q(public=Problem.VIEW_ONLY) | Q(public=Problem.VIEW_SUBMIT)))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @check_permissions('problem.add_problem')
    def create(self, request):
        serializer = ProblemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response(msg('Successful create.'))

    @check_permissions('problem.change_problem')
    def update(self, request, *args, **kwargs):
        problem = self.get_object()
        serializer = ProblemSerializer(problem, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response(msg('Successful update.'))

    @check_permissions('problem.delete_problem')
    def destroy(self, request, *args, **kwargs):
        problem = self.get_object()
        problem.delete()
        return Response(msg('Successful delete.'))

    def retrieve(self, request, *args, **kwargs):
        problem = self.get_object()
        serializer = ProblemSerializer(problem)
        return Response(msg(serializer.data))

    def get_serializer_class(self):
        if self.action == 'list':
            return ProblemListSerializer
        else:
            return self.serializer_class


def handle_uploaded_file(f, origin_filename):
    suffix = origin_filename.split('.')[-1]
    filename = str(uuid4()) + '.' + suffix
    path = os.path.join(PROBLEM_IMAGE_DIR, filename)
    if not os.path.exists(PROBLEM_IMAGE_DIR) or not os.path.isdir(PROBLEM_IMAGE_DIR):
        os.makedirs(PROBLEM_IMAGE_DIR)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    img: Image.Image = Image.open(path)
    (w, h) = img.size
    if w > 1000 or h > 1000:
        nw = nh = 1000
        if w > h:
            nh = nw * h // w
        else:
            nw = nh * w // h
        img2 = img.resize((nw, nh))
        img.close()
        img2.save(path)
        img2.close()
    else:
        img.close()
    return filename


class ProblemImageAPI(APIView):
    def get(self, request, *args, **kwargs):
        form = ImageNameForms(request.GET)
        if form.is_valid():
            path = os.path.join(PROBLEM_IMAGE_DIR, str(form.cleaned_data['title']))
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return HttpResponse(f.read())
        return HttpResponse('', status=404)

    @check_permissions('problem.add_problem')
    def put(self, request, *args, **kwargs):
        form = UploadImageForms(request.POST, request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.FILES['file'], str(request.FILES['file']))
            return Response(msg(f'/api/problem/image?title={filename}'))
        return Response(msg(err=form.errors))

    @check_permissions('problem.add_problem')
    def delete(self, request, *args, **kwargs):
        form = ImageNameForms(request.GET)
        if form.is_valid():
            title = form.cleaned_data['title']
            path = os.path.join(PROBLEM_IMAGE_DIR, str(title))
            if os.path.exists(path):
                os.remove(path)
                return Response(msg('Ok'))
            return Response(msg(err='file not exist.'))
        return Response(msg(err=form.errors))
