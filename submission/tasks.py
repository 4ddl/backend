import platform

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from submission.config import Verdict, Language
from submission.models import Submission
from ddl.settings import PROBLEM_TEST_CASES_DIR
from ddlcw import Runner


@shared_task
def run_submission_task(pk):
    try:
        submission = Submission.objects.get(id=pk)
        if platform.system() != 'Linux':
            submission.verdict = Verdict.SYSTEM_ERROR
            submission.additional_info = 'Linux platform required.'
        else:
            submission.verdict = Verdict.ACCEPTED
            submission.time_spend = 1000
            submission.memory_spend = 3
            submission.save()
            runner = Runner(
                PROBLEM_TEST_CASES_DIR,
                submission.problem.manifest,
                submission.problem.time_limit,
                submission.problem.memory_limit,
                submission.code,
                Language.LANGUAGE_CONFIG[submission.lang])
            print('compile')
            print(runner.compile())
            print('runner')
            print(runner.run())
    except ObjectDoesNotExist:
        pass
