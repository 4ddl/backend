import platform

from celery import shared_task

from submission.config import Verdict
from submission.models import Submission
from django.core.exceptions import ObjectDoesNotExist


@shared_task
def run_submission_task(pk):
    try:
        submission = Submission.objects.get(id=pk)
        if platform.system() != 'Linux':
            submission.verdict = Verdict.SYSTEM_ERROR
            submission.additional_info = 'Linux platform required.'
        else:
            manifest = submission.problem.manifest
            time_limit = submission.problem.time_limit
            memory_limit = submission.problem.memory_limit
            code = submission.code
            submission.verdict = Verdict.ACCEPTED
            submission.time_spend = 1000
            submission.memory_spend = 3
            submission.save()
            print(manifest, time_limit, memory_limit, code)
    except ObjectDoesNotExist:
        pass
