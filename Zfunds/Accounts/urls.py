from django.contrib import admin
from django.urls import path
from Zfunds.Accounts import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="register"),
    path('advisor-user-register', views.AdvisorUserRegisterView.as_view(), name="token"),
    path('login', views.CustomAuthToken.as_view(), name="login"),

]
