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
    author = UserShortSerializer(required=False)

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
                  'last_update']
        depth = 0

    def save(self, user):
        Problem(author=user,
                title=self.validated_data['title'],
                memory_limit=self.validated_data['memory_limit'],
                source=self.validated_data['source'],
                content=self.validated_data['content'],
                time_limit=self.validated_data['time_limit'],
                public=self.validated_data['public']).save()
