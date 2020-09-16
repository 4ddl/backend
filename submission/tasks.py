from celery import shared_task

from submission.models import Submission


# remote run task
@shared_task(name='run_submission_task')
def run_submission_task(submission_id, problem_id, manifest, code, language, time_limit, memory_limit):
    print(submission_id, problem_id, manifest, code, language, time_limit, memory_limit)
    result_submission_task.apply_async(args=[submission_id, 'AC', 100, 20, {}], queue='result')


# call back task
@shared_task(name='result_submission_task')
def result_submission_task(submission_id, verdict, time_cost, memory_cost, additional_info):
    submission = Submission.objects.get(id=submission_id)
    submission.verdict = verdict
    submission.time_cost = time_cost
    submission.memory_cost = memory_cost
    submission.additional_info = additional_info
    submission.save()
