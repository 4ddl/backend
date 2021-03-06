from rest_framework import serializers

from problem.models import Problem


class ProblemShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title']


class ProblemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id',
                  'title',
                  'total_accepted',
                  'total_submitted',
                  'public',
                  'author',
                  'source',
                  'create_time',
                  'last_update']
        depth = 0


class ProblemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id',
                  'title',
                  'content',
                  'time_limit',
                  'memory_limit',
                  'public',
                  'source',
                  'manifest']

    def save(self, user):
        Problem(creator=user,
                title=self.validated_data['title'],
                memory_limit=self.validated_data['memory_limit'],
                source=self.validated_data['source'],
                content=self.validated_data['content'],
                time_limit=self.validated_data['time_limit'],
                manifest=self.validated_data['manifest'],
                public=self.validated_data['public']).save()


class ProblemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id',
                  'title',
                  'content',
                  'time_limit',
                  'memory_limit',
                  'public',
                  'source',
                  'manifest']


class ProblemSerializer(serializers.ModelSerializer):
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


class ProblemFileSerializer(serializers.Serializer):
    title = serializers.CharField()


class ProblemTestCasesSerializer(serializers.Serializer):
    file = serializers.FileField()


class ProblemPDFSerializer(serializers.Serializer):
    file = serializers.FileField()


class ProblemImageSerializer(serializers.Serializer):
    file = serializers.ImageField()


class ProblemImportSerializer(serializers.Serializer):
    file = serializers.FileField()
