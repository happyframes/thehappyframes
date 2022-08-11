from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterAPI.as_view()),
    path('verify_otp/', VerifyOTPAPI.as_view()),
]
