from django.db import models

# Create your models here.
from django.db import models
from user.models import User
from problem.models import Problem


class SubmissionModel(models.Model):
    class Language:
        C = 0
        CPP = 1
        JAVA = 2
        PYTHON = 3

    class Verdict:
        PENDING = -1
        ACCEPT = 0
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
        (Verdict.ACCEPT, 'Accepted'),
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

    user = models.ForeignKey(User, models.CASCADE, verbose_name='提交用户')
    code = models.TextField(verbose_name="源码")
    problem = models.ForeignKey(Problem, models.CASCADE, verbose_name='提交题目')
    verdict = models.IntegerField(default=-1, choices=verdict_choice, verbose_name='结果')
    lang = models.IntegerField(default=Language.C, verbose_name='提交语言')
    create_time = models.DateTimeField(auto_now=True, verbose_name='提交时间')
    time_spend = models.BigIntegerField(default=0, verbose_name='时间花费')
    memory_spend = models.BigIntegerField(default=0, verbose_name='内存花费')

    class Meta:
        verbose_name = '判题数据'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'<Submission>id:{self.id} problem: {self.problem.id} verdict: {self.verdict}'
