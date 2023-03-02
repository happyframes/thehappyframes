from django.urls import path
from orders.views import OrdersAPI, UserOrdersAPI, AllOrdersAPI, DeleteOrdersAPI


urlpatterns = [
    path('photos/', OrdersAPI.as_view()),
    path('my_orders/', UserOrdersAPI.as_view()),
    path('all_orders/<int:page>/', AllOrdersAPI.as_view()),
    path('delete_orders/', DeleteOrdersAPI.as_view()),
]
