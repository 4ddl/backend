from rest_framework import serializers

from problem.serializers import ProblemShortSerializer
from user.models import User
from user.serializers import UserShortSerializer
from .models import Submission


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
            'time_spend',
            'memory_spend'
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
            'time_spend',
            'memory_spend',
            'additional_info'
        )


# create submission serializer
class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = (
            'code',
            'problem',
            'lang',
        )

    def save(self, user: User):
        submission = Submission(
            user=user,
            code=self.validated_data['code'],
            problem=self.validated_data['problem'],
            lang=self.validated_data['lang'],
        )
        submission.save()
        return submission
