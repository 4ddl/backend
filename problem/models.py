from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from user.models import User
from submission.config import Verdict


# Create your models here.

class Problem(models.Model):
    VIEW_SUBMIT = 0
    VIEW_ONLY = 1
    DISABLE = 2
    PUBLIC_CHOICES = [
        (VIEW_SUBMIT, 'Allow view and submit'),
        (VIEW_ONLY, 'Allow view'),
        (DISABLE, 'Disabled'),
    ]
    title = models.CharField(max_length=100, null=False, blank=False)
    content = JSONField()
    time_limit = models.IntegerField(default=0, null=False, blank=False)
    memory_limit = models.IntegerField(default=0, null=False, blank=False)
    public = models.IntegerField(default=VIEW_SUBMIT, choices=PUBLIC_CHOICES, null=False, blank=False)
    source = models.CharField(max_length=100, null=False, blank=False)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    last_update = models.DateTimeField(auto_now=True, editable=False)
    test_cases = ArrayField(models.CharField(max_length=100, null=False, blank=False), blank=True, default=None)

    def __str__(self):
        return f'{self.id}-{self.title}'

    @property
    def accepted_submissions(self):
        return self.submissions.filter(verdict=Verdict.ACCEPTED).count()

    @property
    def total_submissions(self):
        return self.submissions.count()

    class Meta:
        ordering = ['id']
