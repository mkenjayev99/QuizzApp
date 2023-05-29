from datetime import timedelta
from operator import attrgetter

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from account.models import Account
from account.serializers import AccountSerializer
from .models import Option, Category, Quizz, Question, Contact
from .serializers import (CategorySerializer, QuestionSerializer,
                          ResultSerializer, ContactSerializer)


class CategoryListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/api/quizz/category
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class QuestionListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/api/quizz/category/{category_id}/questions/
    serializer_class = QuestionSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        qs = Question.objects.filter(category_id=category_id).order_by('?')[:5]
        return qs

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     category_id = self.kwargs.get('category_id')
    #     if qs:
    #         qs = qs.filter(category_id=category_id)
    #         return qs
    #     return HttpResponseNotFound('Not Found!')


class ResultListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/api/quizz/quizz-result

    queryset = Quizz.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = sorted(qs, key=attrgetter('score'), reverse=True)
        return qs


class ResultCreateAPIView(APIView):
    # http://127.0.0.1:8000/api/quizz/quizz-create

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the category.'
                ),
                'questions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question_id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID of the question.'
                            ),
                            'answers_id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID of the answer.'
                            ),
                        }
                    )
                )
            },
            required=['category_id', 'questions'],
            example={
                "category_id": 1,
                "questions": [
                    {
                        "question_id": 1,
                        "option_id": 1
                    },
                    {
                        "question_id": 2,
                        "option_id": 1
                    },
                    {
                        "question_id": 3,
                        "option_id": 1
                    },
                    {
                        "question_id": 7,
                        "option_id": 1
                    }
                ]
            }
        )
    )
    def post(self, request):
        count = 0
        account = self.request.user
        category_id = self.request.data.get('category_id')
        questions = self.request.data.get('questions')
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response("Category not found")
        result = Quizz.objects.create(account_id=account.id, category_id=category_id)
        for i in questions:
            question_id = int(i.get('question_id'))
            option_id = int(i.get('option_id'))
            try:
                question = Question.objects.get(id=question_id)
                option = Option.objects.get(id=option_id)
            except (Question.DoesNotExist, Option.DoesNotExist):
                continue
            if option.is_true:
                count += 10
            result.questions.add(question)
        result.score = count
        result.save()
        print(Response("Result was saved", status=status.HTTP_201_CREATED))
        return Response("Result was saved", status=status.HTTP_201_CREATED)

    """
    Example for sending data:
    
    {
      "category_id": 1,
      "questions": [
        {
          "question_id": 1,
          "option_id": 1
        },
        {
          "question_id": 2,
          "option_id": 6
        }
      ]
    }
    """


# class ResultByTime(APIView):
#     permission_classes = [permissions.IsAdminUser]
#
#     @staticmethod
#     def get(request):
#         time_period = request.GET.get('time_period', 'day')
#
#         if time_period == 'day':
#             trunc_func = TruncDay('created_date')
#         elif time_period == 'week':
#             trunc_func = TruncWeek('created_date')
#         elif time_period == 'month':
#             trunc_func = TruncMonth('created_date')
#         else:
#             return Response("Invalid time_period parameter", status=status.HTTP_400_BAD_REQUEST)
#
#         results = Quizz.objects.annotate(
#             result_count=Count('id'),
#             average_score=Avg('score'),
#             truncated_date=trunc_func,
#         ).values('truncated_date', 'result_count', 'average_score')
#
#         return Response(results, status=status.HTTP_200_OK)


class AverageStatisticsListByCategory(APIView):
    # http://127.0.0.1:8000/api/quizz/result-by-category/

    def get(self, request):
        categories = Category.objects.all()
        category_results = []
        for category in categories:
            average_by_category = Quizz.calculate_average_result_category(category)
            if average_by_category is not None:
                rounded_average = round(average_by_category, 2)
                category_results.append({'title': category.title, 'average_result': rounded_average})
            else:
                category_results.append({'title': category.title, 'average_result': average_by_category})
        return Response(category_results)


class AverageStatisticsListByAccount(APIView):
    # http://127.0.0.1:8000/api/quizz/result-by-account

    def get(self, request):
        accounts = Account.objects.all()
        account_results = []
        for account in accounts:
            average_by_account = Quizz.calculate_average_result_account(account)
            serialized_account = AccountSerializer(account).data
            if average_by_account is not None:
                rounded_average = round(average_by_account, 2)
                account_results.append({"account": serialized_account, "average_by_account": rounded_average})
            else:
                account_results.append({"account": serialized_account, "average_by_account": average_by_account})

            return Response(account_results)


# class StatisticsAPIView(APIView):
#     permission_classes = [permissions.IsAdminUser]
#
#     @staticmethod
#     def get(request):
#         categories = Category.objects.all()
#         authors = Account.objects.all()
#
#         statistics = {
#             'authors': authors,
#             'categories': categories,
#             'results': Quizz.objects.all()
#         }
#
#         serializer = StatisticsSerializer(statistics, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

class DayStatisticsListAPIview(generics.ListAPIView):
    queryset = Quizz.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = Quizz.objects.annotate(day=TruncDay('created_date')).filter(day=timezone.now().date()).annotate(
            total_results=Count('id'))
        return qs


class WeekStatisticsListAPIView(generics.ListAPIView):
    queryset = Quizz.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        now = timezone.now().date()
        past_week = now - timedelta(days=7)
        qs = Quizz.objects.filter(created_date__range=[past_week, now]).annotate(total_results=Count('id'))
        return qs


class MonthStatisticsListAPIView(generics.ListAPIView):
    queryset = Quizz.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        now = timezone.now().date()
        past_month = now - timedelta(days=30)
        qs = Quizz.objects.filter(created_date__range=[past_month, now]).annotate(total_results=Count('id'))
        return qs


class ContactListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
