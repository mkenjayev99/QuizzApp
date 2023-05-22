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
    option = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Quizz
        fields = ['id', 'student', 'category', 'questions', 'option', 'score']
        extra_kwargs = {
            'score': {'read_only': True}
        }


class StatisticsSerializer(serializers.ModelSerializer):
    authors = MyProfileSerializer(many=True)
    results = ResultSerializer(many=True)

    class Meta:
        model = Quizz
        fields = ['authors', 'results']



