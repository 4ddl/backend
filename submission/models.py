# Create your models here.
from django.db import models
from user.models import User
from problem.models import Problem
from submission.config import Verdict, Language


class Submission(models.Model):
    verdict_choice = (
        (Verdict.PENDING, 'Pending'),
        (Verdict.ACCEPTED, 'Accepted'),
        (Verdict.PRESENTATION_ERROR, 'Presentation Error'),
        (Verdict.TIME_LIMIT_EXCEEDED, 'Time Limit Exceeded'),
        (Verdict.MEMORY_LIMIT_EXCEEDED, 'Memory Limit Exceeded'),
        (Verdict.WRONG_ANSWER, 'Wrong Answer'),
        (Verdict.RUNTIME_ERROR, 'Runtime Error'),
        (Verdict.OUTPUT_LIMIT_EXCEEDED, 'Output Limit Exceeded'),
        (Verdict.COMPILE_ERROR, 'Compile Error'),
        (Verdict.SYSTEM_ERROR, 'System Error'),
    )

    lang_choice = (
        (Language.C, "gcc"),
        (Language.CPP, "g++"),
        (Language.JAVA, "java"),
        (Language.PYTHON, "python")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    verdict = models.IntegerField(default=-1, choices=verdict_choice)
    lang = models.IntegerField(default=Language.C)
    create_time = models.DateTimeField(auto_now_add=True)
    time_spend = models.IntegerField(default=0)
    memory_spend = models.IntegerField(default=0)

    def __str__(self):
        return f'<Submission>id:{self.id} problem: {self.problem.id} verdict: {self.verdict}'
