from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('my_profile/<int:pk>', views.MyProfileRUDAPIView.as_view()),
]
