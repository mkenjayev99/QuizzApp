from django.urls import path
from . import views

urlpatterns = [
    path('category/<int:pk>/', views.CategoryListAPIView.as_view()),
    path('category/<int:pk>/questions/', views.QuestionListAPIView.as_view()),
    path('category/<int:pk>/questions/<int:question_id>/options/', views.OptionListCreate.as_view()),

    path('quizz-result/<int:pk>/', views.ResultListAPIView.as_view()),
    path('quizz-create/', views.ResultCreateAPIView.as_view()),

    path('result-by-time/', views.ResultByTime.as_view()),
    path('result-by-category/', views.StudentAverageStatisticsByCategory.as_view()),
]


