from rest_framework import serializers
from .models import Submission
from user.serializers import UserShortSerializer


class SubmissionSerializers(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = (
            'id',
            'user',
            'problem',
            'verdict',
            'language',
            'create_time',
            'time_spend',
            'memory_spend'
        )
        read_only_fields = (
            'create_time',
        )
