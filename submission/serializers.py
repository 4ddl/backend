from rest_framework import serializers

from problem.serializers import ProblemShortSerializer
from submission.config import Language
from user.models import User
from user.serializers import UserShortSerializer
from .models import Submission
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from problem.models import Problem


# list submission serializer
class SubmissionShortSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    problem = ProblemShortSerializer()

    class Meta:
        model = Submission
        fields = (
            'id',
            'user',
            'problem',
            'create_time',
            'verdict',
            'lang',
            'time_cost',
            'memory_cost'
        )


# basic submission serializer
class SubmissionSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    problem = ProblemShortSerializer()

    class Meta:
        model = Submission
        fields = (
            'id',
            'user',
            'code',
            'problem',
            'verdict',
            'lang',
            'create_time',
            'time_cost',
            'memory_cost',
            'additional_info'
        )


# create submission serializer
class SubmissionCreateSerializer(serializers.ModelSerializer):
    lang = serializers.ChoiceField(choices=Language.LANGUAGE_CHOICES)

    class Meta:
        model = Submission
        fields = (
            'code',
            'problem',
            'lang',
        )

    @staticmethod
    def validate_problem(value):
        try:
            problem = value
            if problem.public == Problem.VIEW_SUBMIT:
                return value
            else:
                raise serializers.ValidationError(_('problem read only.'))
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('problem not exist.'))

    def save(self, user: User):
        submission = Submission(
            user=user,
            code=self.validated_data['code'],
            problem=self.validated_data['problem'],
            lang=self.validated_data['lang'],
        )
        submission.save()
        return submission
