from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.

class Problem(models.Model):
    VIEW_SUBMIT = 0
    VIEW_ONLY = 1
    DISABLE = 2
    PUBLIC_CHOICES = [
        (0, 'Allow view and submit'),
        (1, 'Allow view'),
        (2, 'Disabled'),
    ]
    title = models.CharField(max_length=100, null=False, blank=False)
    content = JSONField()
    time_limit = models.IntegerField(default=0, null=False, blank=False)
    memory_limit = models.IntegerField(default=0, null=False, blank=False)
    public = models.IntegerField(default=VIEW_SUBMIT, choices=PUBLIC_CHOICES, null=False, blank=False)
    source = models.CharField(max_length=100, null=False, blank=False)

    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    last_update = models.DateTimeField(auto_now=True, editable=False)
