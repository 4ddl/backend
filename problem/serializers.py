from rest_framework import serializers
from problem.models import Problem
from user.serializers import UserShortSerializer


class ProblemShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title']


class ProblemListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = Problem
        fields = ['id',
                  'title',
                  'accepted_submissions',
                  'total_submissions',
                  'public',
                  'author',
                  'source',
                  'create_time']
        depth = 0


class ProblemSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = Problem
        fields = ['id',
                  'title',
                  'content',
                  'time_limit',
                  'memory_limit',
                  'public',
                  'source',
                  'author',
                  'create_time',
                  'test_cases',
                  'last_update']
        read_only_fields = [
            'create_time',
            'last_update',
            'test_cases'
        ]
        depth = 0
