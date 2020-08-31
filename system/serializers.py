from rest_framework import serializers
from ddl.settings import LANGUAGES


class LanguageSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=LANGUAGES)
