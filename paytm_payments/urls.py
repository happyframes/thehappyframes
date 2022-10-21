from django.urls import path
from paytm_payments.views import StartPaymentAPI, HandlePaymentAPI

urlpatterns = [
    path('pay/', StartPaymentAPI.as_view(), name="start_payment"),
    path('handle_payment/', HandlePaymentAPI.as_view(), name="handle_payment"),
]