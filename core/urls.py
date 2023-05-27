from django.urls import path
from . import views

urlpatterns = [
    path('category', views.CategoryListAPIView.as_view()),
    path('category/<int:category_id>/questions/', views.QuestionListAPIView.as_view()),

    path('quizz-result/', views.ResultListAPIView.as_view()),
    path('quizz-create/', views.ResultCreateAPIView.as_view()),

    path('result-by-category/', views.AverageStatisticsListByCategory.as_view()),
    path('result-by-account/', views.AverageStatisticsListByAccount.as_view()),

    path('result-by-day/', views.DayStatisticsListAPIview.as_view()),
    path('result-by-week/', views.WeekStatisticsListAPIView.as_view()),
    path('result-by-month/', views.MonthStatisticsListAPIView.as_view()),

    path('contact/', views.ContactListCreateAPIView.as_view()),
]


