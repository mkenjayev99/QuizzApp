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


class ResultListCreate(generics.GenericAPIView):

    def post(self, request):
        data = self.request.data.get('data')
        """
        [
            'object': {'id': 1
                item: 
                {'question_id': 1    <- 1 - item
                'option_id': 4
                }
                    },
            
            {'question_id': 3    <- 2 - item
            'option_id': 1
            },
            
            {'question_id': 12    <- 3 - item
            'option_id': 45
            },
            
            {'question_id': 19    <- 4 - item
            'option_id': 34
            },
            
            {'question_id': 20    <- 5 - item
            'option_id': 10
            },
        ]
        """
        question_id = data.object.item['question_id']
        option_id = data.object.item['option_id']

        right = 0
        wrong = 0
        score = 0
        # if self.kwargs.get('question_id') == question_id and self.










