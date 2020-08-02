from rest_framework import serializers
from .models import Submission
from user.serializers import UserShortSerializer
from user.models import User
from problem.serializers import ProblemShortSerializer


class SubmissionSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    problem = ProblemShortSerializer(read_only=True)

    @staticmethod
    def validate_lang(value):
        for lang in Submission.lang_choice:
            if lang[0] == value:
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
