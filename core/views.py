from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Option, Category, Quizz, Question
from .permissions import IsOwnerOrReadOnly
from .serializers import (StatisticsSerializer,
                          ResultSerializer,
                          CategorySerializer,
                          OptionSerializer,
                          QuestionSerializer
                          )


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionListAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        qs = Question.objects.filter(category_id=category_id).order_by('?')[:5]
        return qs

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     category_id = self.kwargs.get('category_id')
    #     if qs:
    #         qs = qs.filter(category_id=category_id)
    #         return qs
    #     return HttpResponseNotFound('Not Found!')


class OptionListCreate(generics.ListCreateAPIView):
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ returns the queryset of options of exact question """

        question_id = self.kwargs.get('question_id')
        qs = Option.objects.filter(question_id=question_id)
        return qs


class ResultListCreate(generics.ListAPIView):
    serializer_class = ResultSerializer
    queryset = Quizz.objects.all()








