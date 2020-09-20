import json
import os
import traceback
import zipfile
from json import JSONDecodeError

from django.http import HttpResponse
from django.utils.translation import gettext as _

from oj.settings import PROBLEM_TEST_CASES_DIR, TMP_DIR


class ManifestError(Exception):
    pass


# 检查test case是否正确
def validate_test_case(dir_name, filename):
    if not os.path.exists(PROBLEM_TEST_CASES_DIR) or not os.path.isdir(PROBLEM_TEST_CASES_DIR):
        raise ManifestError(_('problem test cases dir not exist'))
    problem_test_case_dir = os.path.join(PROBLEM_TEST_CASES_DIR, dir_name)
    if not os.path.exists(problem_test_case_dir) or not os.path.isdir(problem_test_case_dir):
        raise ManifestError(_('this problem test case dir not exist'))
    file_path = os.path.join(problem_test_case_dir, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise ManifestError(_('this problem test case dir not exist'))
    if not os.access(file_path, os.R_OK):
        raise ManifestError(_('file "{file_path}" not readable.').format(file_path=file_path))


# 检查manifest是否正确
def validate_manifest(manifest):
    # check manifest type
    if isinstance(manifest, str):
        try:
            manifest = json.loads(manifest)
        except JSONDecodeError:
            raise ManifestError(_('decode manifest error'))
    if not isinstance(manifest, dict):
        raise ManifestError(_('manifest type error, type(manifest)={type_of_manifest}').format(type(manifest)))
    # check manifest keys
    keys = ['hash', 'test_cases', 'spj']
    for key in keys:
        if key not in manifest.keys():
            raise ManifestError(_('key {key} not in manifest').format(key=key))
    # check manifest key-values type
    if not isinstance(manifest.get('hash'), str):
        raise ManifestError(_('hash value not str'))
    if len(manifest.get('hash')) == 0:
        raise ManifestError(_('hash value length 0'))
    if not isinstance(manifest.get('test_cases'), list):
        raise ManifestError(_('test_cases value not list'))
    if not isinstance(manifest.get('spj'), bool):
        raise ManifestError(_('spj value not bool'))
    if manifest.get('spj'):
        if 'spj_code' not in manifest.keys() or not isinstance(manifest.get('spj_code'), str):
            raise ManifestError(_('spj_code value not str'))
    # check test_cases
    for item in manifest.get('test_cases'):
        if not isinstance(item, dict):
            raise ManifestError(_('test_cases item {item} not dict').format(item=item))
        if 'in' not in item.keys():
            raise ManifestError(_('test_cases item needs key "in"'))
        if not isinstance(item.get('in'), str):
            raise ManifestError(_('test_cases item key "in" type error'))
        if len(item.get('in')) == 0:
            raise ManifestError(_('test_cases item key "in" length 0'))
        validate_test_case(manifest.get('hash'), item.get('in'))
        if not manifest.get('spj'):
            if 'out' not in item.keys():
                raise ManifestError(_('test_cases item needs key "out"'))
            if not isinstance(item.get('out'), str):
                raise ManifestError(_('test_cases item key "out" type error'))
            if len(item.get('out')) == 0:
                raise ManifestError(_('test_cases item key "out" length 0'))
            validate_test_case(manifest.get('hash'), item.get('out'))
    return manifest


# 打包test case 并且返回
def package_test_case(valid_manifest):
    try:
        # 生成临时的压缩包
        test_case_dir = os.path.join(PROBLEM_TEST_CASES_DIR, valid_manifest['hash'])
        file_name = f'{valid_manifest["hash"]}.zip'
        temp_file_path = os.path.join(TMP_DIR, file_name)
        download_zipfile = zipfile.ZipFile(temp_file_path, 'w')
        for item in os.listdir(test_case_dir):
            if os.path.isfile(os.path.join(test_case_dir, item)):
                download_zipfile.write(os.path.join(test_case_dir, item), item)
        download_zipfile.close()
        # 构造返回的数据
        f = open(temp_file_path, 'rb')
        response = HttpResponse(f.read(), content_type='application/x-zip-compressed')
        f.close()
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        # 删除临时的压缩包
        os.remove(temp_file_path)
        return response
    except Exception:
        traceback.print_exc()
    return HttpResponse(status=500)
