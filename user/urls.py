from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.LoginApiView.as_view()),
    path('signup/', views.SignupApiView.as_view()),
    path('reset-password/', views.ResetPasswordApiView.as_view()),
    path('update-profile/', views.UpdateProfileApiView.as_view()),
]
