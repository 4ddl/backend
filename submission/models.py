# Create your models here.
from django.db import models
from user.models import User
from problem.models import Problem


class Submission(models.Model):
    class Language:
        C = 0
        CPP = 1
        JAVA = 2
        PYTHON = 3

    class Verdict:
        PENDING = -1
        ACCEPTED = 0
        PRESENTATION_ERROR = 1
        TIME_LIMIT_EXCEEDED = 2
        MEMORY_LIMIT_EXCEEDED = 3
        WRONG_ANSWER = 4
        RUNTIME_ERROR = 5
        OUTPUT_LIMIT_EXCEEDED = 6
        COMPILE_ERROR = 7
        SYSTEM_ERROR = 8

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    verdict = models.IntegerField(default=-1, choices=verdict_choice)
    lang = models.IntegerField(default=Language.C)
    create_time = models.DateTimeField(auto_now_add=True)
    time_spend = models.IntegerField(default=0)
    memory_spend = models.IntegerField(default=0)

    def __str__(self):
        return f'<Submission>id:{self.id} problem: {self.problem.id} verdict: {self.verdict}'
