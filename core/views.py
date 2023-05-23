from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Option, Category, Quizz, Question
from .permissions import IsOwnerOrReadOnly
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

        question_id = self.kwargs.get('question')
        qs = Option.objects.filter(question_id=question_id)
        return qs


# Student attends to take the quizz:
# class ResultCreateAPIView(generics.CreateAPIView):
#     serializer_class = ResultSerializer
#
#     def perform_create(self, serializer):
#         # the Student who is taking the quizz:
#         student = self.request.user
#
#         # handling submitted answers:
#         submitted_options = self.request.user.data.get('options', [])
#
#         # calculating score, wrong, right answers:
#         score = 0
#         score_by_level = 0
#         wrong = 0
#         correct = 0
#
#         all_questions = len(submitted_options)
#         for option in submitted_options:
#             # Check if the option is true or not:
#             question_id = option['question_id']
#             chosen_option_id = option['chosen_option_id']
#             is_true = Option.objects.get(question_id=question_id, id=chosen_option_id).is_true
#             if is_true:
#                 if option.question.level == 0:
#                     score_by_level += 10
#                 elif option.question.level == 1:
#                     score_by_level += 20
#                 else:
#                     score_by_level += 40
#                 score += 10
#                 correct += 1
#             elif not is_true:
#                 wrong += 1
#         percentage = (correct/all_questions)*100
#
#         # Saving the result above:
#         serializer.save(
#             student=student,
#             category_id=self.kwargs['category_id'],
#             score=score,
#             correct=correct,
#             wrong=wrong,
#             percentage=percentage
#         )
#         return Response('Successfully created')

class ResultCreateAPIView(APIView):
    def post(self,  request):
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
            if option.is_correct:
                count += 20
            result.questions.add(question)
        result.result = count
        result.save()
        return Response("Result was saved")


class ResultListAPIView(generics.ListAPIView):
    queryset = Quizz.objects.all()
    serializer_class = ResultSerializer
