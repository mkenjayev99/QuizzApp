from rest_framework import generics, status, permissions
from rest_framework.response import Response
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


# Student attends to take the quizz:
class ResultCreateAPIView(generics.CreateAPIView):
    serializer_class = ResultSerializer

    def perform_create(self, serializer):
        # the Student who is taking the quizz:
        student = self.request.user

        # handling submitted answers:
        submitted_options = self.request.user.data.get('options', [])

        # calculating score, wrong, right answers:
        score = 0
        score_by_level = 0
        wrong = 0
        correct = 0

        all_questions = len(submitted_options)
        for option in submitted_options:
            # Check if the option is true or not:
            question_id = option['question_id']
            chosen_option_id = option['chosen_option_id']
            is_true = Option.objects.get(question_id=question_id, id=chosen_option_id).is_true
            if is_true:
                if option.question.level == 0:
                    score_by_level += 10
                elif option.question.level == 1:
                    score_by_level += 20
                else:
                    score_by_level += 40
                score += 10
                correct += 1
            elif not is_true:
                wrong += 1
        percentage = (correct/all_questions)*100

        # Saving the result above:
        serializer.save(
            student=student,
            category_id=self.kwargs['category_id'],
            score=score,
            correct=correct,
            wrong=wrong,
            percentage=percentage
        )
        return Response('Successfully created')


class ResultListAPIView(generics.ListAPIView):
    serializer_class = ResultSerializer

    def get_queryset(self):
        student = self.request.user
        category_id = self.kwargs['category_id']
        return Quizz.objects.filter(student=student, category_id=category_id)
