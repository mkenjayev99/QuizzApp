from rest_framework import serializers

from account.serializers import MyProfileSerializer
from .models import Question, Category, Option, Quizz


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'title', 'is_true']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'category', 'question', 'options', 'level']
        extra_kwargs = {
            'category': {'read_only': True}
        }


class ResultSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(read_only=True)
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Quizz
        fields = ['id', 'student', 'category', 'questions', 'options', 'score']
        extra_kwargs = {
            'score': {'read_only': True}
        }


class StatisticsSerializer(serializers.ModelSerializer):
    authors = MyProfileSerializer(many=True)

    results = ResultSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        request = self.context.get('request')
        category_id = request.query_params.get('category_id')

        if category_id:
            results = instance.results.filter(category_id=category_id)
        else:
            results = instance.results.all()

        serialized_results = ResultSerializer(results, many=True).data

        return {
            'authors': MyProfileSerializer(instance.authors, many=True).data,
            'results': serialized_results
        }

    class Meta:
        model = Quizz
        fields = ['authors', 'results']



