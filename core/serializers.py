from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import Question, Category, Option, Account, Quizz
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=218)
    password2 = serializers.CharField(max_length=218)

    class Meta:
        model = Account
        fields = ['username', 'password', 'password2', 'first_name', 'last_name', 'image', 'bio', 'date_created']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password does not match! Try again.")
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        return Account.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=218, required=True)
    password = serializers.CharField(max_length=218, write_only=True)
    tokens = serializers.SerializerMethodField(read_only=True)

    def get_tokens(self, obj):
        username = obj.get('username')
        tokens = Account.objects.get(username=username).tokens
        return tokens

    class Meta:
        model = Account
        fields = ['username', 'password', 'tokens']

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed({'message': "Username or Password wrong, Please try again!"})
        if not user.is_active:
            raise AuthenticationFailed({'message': "Account Disabled"})
        return attrs


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'bio', 'date_created']


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


class ResultSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(read_only=True)

    class Meta:
        model = Quizz
        fields = ['id', 'author', 'questions', 'category', 'result']


class StatisticsSerializer(serializers.ModelSerializer):
    authors = MyProfileSerializer(many=True)
    results = ResultSerializer(many=True)

    class Meta:
        model = Quizz
        fields = ['authors', 'results']



