from rest_framework import serializers
from .models import SubmissionModel
from user.serializers import UserShortSerializer
from user.models import User


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
            'verdict',
            'create_time',
            'time_spend',
            'memory_spend'
        )

    def save(self, user: User):
        SubmissionModel.objects.create(
            user=user,
            code=self.validated_data['code'],
            problem=self.validated_data['problem'],
            lang=self.validated_data['lang'],
        )


