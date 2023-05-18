from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Account, Option, Category, Result, Question
from .permissions import IsOwnerOrReadOnly
from .serializers import (RegisterSerializer,
                          LoginSerializer,
                          MyProfileSerializer,
                          StatisticsSerializer,
                          ResultSerializer,
                          CategorySerializer,
                          OptionSerializer,
                          QuestionSerializer
                          )


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'data': "Account successfully created"}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'tokens': serializer.data}, status=status.HTTP_200_OK)


class MyProfileRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = MyProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]


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


class GetQuestionsAndCollectAnswers(generics.ListCreateAPIView):
    serializer_class = (QuestionSerializer, OptionSerializer)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ returns the queryset of question of exact
        category and options that belong to the question """

        category_id = self.kwargs.get('category_id')
        question_id = self.kwargs.get('question_id')
        qs_options = Option.objects.filter(question_id=question_id)
        qs_questions = Question.objects.filter(category_id=category_id)

        ans = {}
        for question, option in enumerate(qs_questions, qs_options):
            ans[question] = option
        return ans






