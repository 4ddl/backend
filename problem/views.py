import os
from uuid import uuid4

from PIL import Image
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http.response import HttpResponse
from django.utils.translation import gettext as _
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.views import Response

from oj.settings import PROBLEM_IMAGE_DIR, TMP_DIR, PROBLEM_PDF_DIR
from problem import utils
from problem.forms import ImageNameForms, RequestFileForm
from problem.models import Problem
from problem.perm import ManageProblemPermission
from problem.serializers import ProblemSerializer, ProblemListSerializer, ProblemTestCasesSerializer, \
    ProblemCreateSerializer, ProblemImageSerializer, ProblemPDFSerializer, ProblemUpdateSerializer, \
    ProblemImportSerializer
from problem.uploads import TestCasesProcessor, TestCasesError
from system.perm import JudgePermission
from utils.permissions import check_permissions
from utils.response import msg


class ProblemFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name='id', lookup_expr='icontains')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    source = filters.CharFilter(field_name='source', lookup_expr='icontains')

    class Meta:
        model = Problem
        fields = ['id', 'title', 'source']


class ProblemViewSet(viewsets.GenericViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filterset_class = ProblemFilter
    lookup_value_regex = r'\d+'

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

    @check_permissions('problem.manage_problem')
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        return Response(msg(_('Successful create.')))

    @check_permissions('problem.manage_problem')
    def update(self, request, *args, **kwargs):
        problem = self.get_object()
        serializer = self.get_serializer(problem, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(msg(_('Successful update.')))

    @check_permissions('problem.manage_problem')
    def destroy(self, request, *args, **kwargs):
        problem = self.get_object()
        problem.delete()
        return Response(msg(_('Successful delete.')))

    def retrieve(self, request, *args, **kwargs):
        problem = self.get_object()
        if problem.public == Problem.VIEW_SUBMIT or problem.public == Problem.VIEW_ONLY or request.user.is_staff:
            serializer = ProblemSerializer(problem)
            return Response(msg(serializer.data))
        raise PermissionDenied

    @action(detail=True, methods=['get'], permission_classes=[ManageProblemPermission])
    def system_retrieve(self, request, *args, **kwargs):
        problem = self.get_object()
        serializer = ProblemCreateSerializer(problem)
        return Response(msg(serializer.data))

    # judge daemon sync test case
    # 因为这个是给判题机使用的接口，所以不会像其他接口那样返回JSON格式的数据
    @action(detail=True, methods=['get'], permission_classes=[JudgePermission])
    def sync_test_cases(self, request, pk=None, *args, **kwargs):
        try:
            problem = self.get_queryset().get(id=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=404)
        try:
            manifest = utils.validate_manifest(problem.manifest)
            return utils.package_test_case(manifest)
        except utils.ManifestError:
            return HttpResponse(status=500)

    # export problem
    # 导出接口使用原生的HttpResponse
    @action(detail=True, methods=['get'], permission_classes=[ManageProblemPermission], url_path='export')
    def export_problem(self, request, *args, **kwargs):
        # TODO: export problem
        return HttpResponse(msg(_('success')))

    # import problem
    @action(detail=False, methods=['put'], permission_classes=[ManageProblemPermission], url_path='import')
    def import_problem(self, request, *args, **kwargs):
        # TODO: import problem
        return Response(msg('success'))

    def get_serializer_class(self):
        if self.action == 'list':
            return ProblemListSerializer
        elif self.action == 'upload_test_cases':
            return ProblemTestCasesSerializer
        elif self.action == 'update':
            return ProblemUpdateSerializer
        elif self.action == 'create':
            return ProblemCreateSerializer
        elif self.action == 'import_problem':
            return ProblemImportSerializer
        else:
            return self.serializer_class

    @action(detail=False, methods=['post'], permission_classes=[ManageProblemPermission])
    def upload_test_cases(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tmp_file = f'{uuid4()}.zip'
        os.makedirs(TMP_DIR, exist_ok=True)
        with open(os.path.join(TMP_DIR, tmp_file), 'wb') as destination:
            for chunk in serializer.validated_data['file'].chunks(1024):
                destination.write(chunk)
        try:
            manifest = TestCasesProcessor.handle_upload_test_cases(tmp_file, TMP_DIR)
            os.remove(os.path.join(TMP_DIR, tmp_file))
            return Response(msg(manifest))
        except TestCasesError as e:
            return Response(msg(err=str(e)))


class ProblemImageAPI(APIView):
    MAX_SIZE = 800

    def get(self, request, *args, **kwargs):
        form = RequestFileForm(data=request.GET)
        if not form.is_valid():
            return Response(msg(_('Params validate error')))
        path = os.path.join(PROBLEM_IMAGE_DIR, str(form.cleaned_data['title']))
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return HttpResponse(f.read())
        else:
            return Response(msg(err=_('Image not exist.')))

    @check_permissions('problem.manage_problem')
    def put(self, request, *args, **kwargs):
        serializer = ProblemImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 将文件保存到PROBLEM_IMAGE_DIR目录下
        suffix = str(serializer.validated_data['file']).split('.')[-1]
        filename = str(uuid4()) + '.' + suffix
        tmp_path = os.path.join(TMP_DIR, filename)
        if not os.path.exists(TMP_DIR) or not os.path.isdir(TMP_DIR):
            os.makedirs(TMP_DIR)
        final_path = os.path.join(PROBLEM_IMAGE_DIR, filename)

        if not os.path.exists(PROBLEM_IMAGE_DIR) or not os.path.isdir(PROBLEM_IMAGE_DIR):
            os.makedirs(PROBLEM_IMAGE_DIR)
        with open(tmp_path, 'wb') as destination:
            for chunk in serializer.validated_data['file'].chunks(1024):
                destination.write(chunk)
        # 如果上传的图片大小太大的话，就将图片等比例缩放到最大边为self.MAX_SIZE大小
        img: Image.Image = Image.open(tmp_path)
        (w, h) = img.size
        if w > self.MAX_SIZE or h > self.MAX_SIZE:
            nw = nh = self.MAX_SIZE
            if w > h:
                nh = nw * h // w
            else:
                nw = nh * w // h
            img2 = img.resize((nw, nh))
            img.close()
            img2.save(final_path)
            img2.close()
        else:
            img.save(final_path)
            img.close()
        return Response(msg(f'/api/problem/image?title={filename}'))

    @check_permissions('problem.manage_problem')
    def delete(self, request, *args, **kwargs):
        form = ImageNameForms(request.GET)
        if form.is_valid():
            title = form.cleaned_data['title']
            path = os.path.join(PROBLEM_IMAGE_DIR, str(title))
            if os.path.exists(path):
                os.remove(path)
                return Response(msg('Ok'))
            return Response(msg(err=_('file not exist.')))
        return Response(msg(err=form.errors))


class ProblemPDFAPI(APIView):
    def get(self, request, *args, **kwargs):
        form = RequestFileForm(data=request.GET)
        if not form.is_valid():
            return Response(msg(_('Params validate error')))
        path = os.path.join(PROBLEM_PDF_DIR, str(form.cleaned_data['title']))
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return HttpResponse(f.read(), content_type='application/pdf')
        else:
            return Response(msg(err=_('PDF not exist.')))

    @check_permissions('problem.manage_problem')
    def post(self, request, *args, **kwargs):
        serializer = ProblemPDFSerializer(data=request.data)
        serializer.is_valid(True)
        filename = str(uuid4()) + '.pdf'
        final_path = os.path.join(PROBLEM_PDF_DIR, filename)
        if not os.path.exists(PROBLEM_PDF_DIR) or not os.path.isdir(PROBLEM_PDF_DIR):
            os.makedirs(PROBLEM_PDF_DIR)
        with open(final_path, 'wb') as destination:
            for chunk in serializer.validated_data['file'].chunks(1024):
                destination.write(chunk)
        return Response(msg({'title': filename}))
