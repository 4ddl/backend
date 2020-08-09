from celery import shared_task

from submission.models import Submission


@shared_task
def run(pk):
    submission = Submission.objects.get(id=pk)
    manifest = submission.problem.manifest
    time_limit = submission.problem.time_limit
    memory_limit = submission.problem.memory_limit
    code = submission.code
    print(manifest, time_limit, memory_limit, code)
