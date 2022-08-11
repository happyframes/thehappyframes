from django.urls import path
from .views import *


urlpatterns = [
    path('photos/', OrdersAPI.as_view()),
    path('my_orders/', UserOrdersAPI.as_view()),
]
