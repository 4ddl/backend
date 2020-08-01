from rest_framework import serializers
from .models import SubmissionModel
from user.serializers import UserShortSerializer


class SubmissionSerializers(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    @staticmethod
    def validate_lang(value):
        for lang in SubmissionModel.lang_choice:
            if lang[0] == value:
                return value
        raise serializers.ValidationError("Language not supported")

    class Meta:
        model = SubmissionModel
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
            'user',
            'verdict',
            'create_time',
            'time_spend',
            'memory_spend'
        )

