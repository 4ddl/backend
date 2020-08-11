from rest_framework import serializers

from problem.serializers import ProblemShortSerializer
from user.models import User
from user.serializers import UserShortSerializer
from .models import Submission
from .config import Language


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


class SubmissionSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    problem = ProblemShortSerializer(read_only=True)

    @staticmethod
    def validate_lang(value):
        if value in list(map(lambda x: x[0], Language.LANGUAGE_CHOICES)):
            return value
        raise serializers.ValidationError("Language not supported")

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
            'memory_spend'
        )
        read_only_fields = (
            'id',
            'verdict',
            'create_time',
            'time_spend',
            'memory_spend'
        )

    def save(self, user: User):
        Submission.objects.create(
            user=user,
            code=self.validated_data['code'],
            problem=self.validated_data['problem'],
            lang=self.validated_data['lang'],
        )
