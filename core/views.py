from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

from account.models import Account
from .models import Option, Category, Quizz, Question
from .serializers import (StatisticsSerializer,
                          CategorySerializer,
                          OptionSerializer,
                          QuestionSerializer,
                          ResultSerializer,
                          )


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionListAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        category_id = self.kwargs.get('pk')
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


class ResultListAPIView(generics.ListAPIView):
    queryset = Quizz.objects.all()
    serializer_class = ResultSerializer


class ResultCreateAPIView(APIView):
    def post(self, request):
        count = 0
        account = self.request.user
        category_id = self.request.data.get('category_id')
        questions = self.request.data.get('questions')
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response("Category not found")
        result = Quizz.objects.create(student=account, category_id=category_id)
        for i in questions:
            question_id = int(i.get('question_id'))
            option_id = int(i.get('option_id'))
            try:
                question = Question.objects.get(id=question_id)
                option = Option.objects.get(id=option_id)
            except (Question.DoesNotExist, Option.DoesNotExist):
                continue
            if option.is_correct:
                count += 20
            result.questions.add(question)
        result.score = count
        result.save()
        return Response("Result was saved", status=status.HTTP_201_CREATED)


class ResultByTime(APIView):
    permission_classes = [permissions.IsAdminUser]

    @staticmethod
    def get(request):
        time_period = request.GET.get('time_period', 'day')

        if time_period == 'day':
            trunc_func = TruncDay('created_date')
        elif time_period == 'week':
            trunc_func = TruncWeek('created_date')
        elif time_period == 'month':
            trunc_func = TruncMonth('created_date')
        else:
            return Response("Invalid time_period parameter", status=status.HTTP_400_BAD_REQUEST)

        results = Quizz.objects.annotate(
            result_count=Count('id'),
            average_score=Avg('score'),
            truncated_date=trunc_func,
        ).values('truncated_date', 'result_count', 'average_score')

        return Response(results, status=status.HTTP_200_OK)


class StudentAverageStatisticsByCategory(APIView):

    def get(self, request):
        student = self.request.user
        category_id = request.GET.get('category_id')

        if not category_id:
            return Response("category_id parameter is required", status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response("Category not found", status=status.HTTP_404_NOT_FOUND)

        results = Quizz.objects.filter(student=student, category=category).annotate(
            average_score=Avg('score')
        )

        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StatisticsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @staticmethod
    def get(request):
        categories = Category.objects.all()
        authors = Account.objects.all()

        statistics = {
            'authors': authors,
            'categories': categories,
            'results': Quizz.objects.all()
        }

        serializer = StatisticsSerializer(statistics, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
