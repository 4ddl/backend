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
            submission.verdict = Verdict.ACCEPTED
            submission.time_spend = 1000
            submission.memory_spend = 3
            submission.save()
    except ObjectDoesNotExist:
        pass
