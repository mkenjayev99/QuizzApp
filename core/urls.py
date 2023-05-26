from django.urls import path
from . import views

urlpatterns = [
    path('category', views.CategoryListAPIView.as_view()),
    path('category/<int:category_id>/questions/', views.QuestionListAPIView.as_view()),

    path('quizz-result/<int:category_id>/', views.ResultListAPIView.as_view()),
    path('quizz-create/', views.ResultCreateAPIView.as_view()),

    path('result-by-time/', views.ResultByTime.as_view()),
    path('result-by-category/', views.StudentAverageStatisticsByCategory.as_view()),
]


