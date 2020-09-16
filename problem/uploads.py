import hashlib
import os
import zipfile

from django.utils.translation import gettext as _

from ddl.settings import PROBLEM_TEST_CASES_DIR


class TestCasesError(Exception):
    pass


class TestCasesProcessor(object):

    @staticmethod
    def handle_upload_test_cases(filename, tmp_path, spj: bool):
        # 检查在临时文件夹存放的zip文件是否格式正确
        if not zipfile.is_zipfile(os.path.join(tmp_path, filename)):
            raise TestCasesError(_('not zip file'))
        zf = zipfile.ZipFile(os.path.join(tmp_path, filename))
        if len(zf.namelist()) == 0:
            raise TestCasesError(_('zip without files.'))
        index = 1
        in_list = []
        out_list = []
        test_cases = []

        while True:
            if spj and f'{index}.in' in zf.namelist():
                in_list.append(f'{index}.in')
                test_cases.append({'in': f'{index}.in'})
            elif not spj and f'{index}.in' in zf.namelist() and f'{index}.out' in zf.namelist():
                in_list.append(f'{index}.in')
                out_list.append(f'{index}.out')
                test_cases.append({
                    'in': f'{index}.in',
                    'out': f'{index}.out'
                })
            else:
                break
            index += 1

        if (spj and len(zf.namelist()) != len(in_list)) or (
                not spj and len(zf.namelist()) != len(in_list) + len(out_list)):
            raise TestCasesError(_('do not put irrelevant files into zip'))

        # 将临时文件夹存放的zip解压到正式的文件里面
        hash_val = hashlib.sha256()
        with open(os.path.join(tmp_path, filename), 'rb') as f:
            hash_val.update(f.read(1024))
        test_case_id = hash_val.hexdigest()
        test_case_dir = os.path.join(PROBLEM_TEST_CASES_DIR, test_case_id)
        os.makedirs(test_case_dir, exist_ok=True)
        manifest = {
            'hash': test_case_id,
            'test_cases': test_cases,
            'spj': spj,
        }
        for item in zf.namelist():
            with open(os.path.join(test_case_dir, item), 'wb') as des:
                content = zf.read(item).replace(b"\r\n", b"\n")
                if item.endswith('.out'):
                    content = content.rstrip()
                des.write(content)
            os.chmod(os.path.join(test_case_dir, item), 0o640)
        return manifest
