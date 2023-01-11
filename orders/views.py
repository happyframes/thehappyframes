import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.serializers import AddressSerializer, UserOrdersDeserializer, UserOrders
from loginApp.models import UserDetails
from .models import Photos, Orders
from loginApp.serializers import RegisterSerializer
from django.db.models import F
from utilities import Success, Failure, FailureSerializer
from django.core.paginator import Paginator

# import logging
# logging.basicConfig(handlers=[logging.FileHandler(filename="log_records.log",
#                                                   encoding='utf-8', mode='a+')], level=logging.DEBUG)


class OrdersAPI(APIView):
    def post(self, request):
        try:
            serializer = AddressSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = UserDetails.objects.update_or_create(
                    email=serializer.validated_data['email'],
                    defaults={"full_name": serializer.validated_data['full_name'],
                              "mobile": serializer.validated_data['mobile'],
                              "address": serializer.validated_data['address']}
                )
                order_count = Orders.objects.all().count()
                if not order_count:
                    order_id = str(1) + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                else:
                    order_id = str(order_count + 1) + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                order = Orders.objects.create(
                    order_id=int(order_id),
                    user=user[0],
                    order_total=serializer.validated_data['order_total'],
                    is_paid=serializer.validated_data['is_paid'],
                    order_state_id=1
                )
                photos = serializer.validated_data['photos']
                for photo in photos:
                    photos_data = Photos.objects.create(
                        photo=photo,
                        tile=serializer.validated_data['tile'],
                        order=order
                    )
                user_order = Orders.objects.filter(order_id=order.order_id).values(
                    'order_id',
                    'order_total',
                    'ordered_date',
                    'delivered_date',
                    'is_paid',
                    order_status=F('order_state__state'),
                    full_name=F('user__full_name'),
                    phone_number=F('user__mobile'),
                    email=F('user__email'),
                    address=F('user__address')
                ).first()
                photos_obj = Photos.objects.filter(order_id=order.order_id)
                tile = photos_obj.values_list('tile', flat=True).distinct()[0]
                user_order.update(photos=list(photos), tile=tile)
                address = user_order["address"].replace('null', 'None')
                user_order["address"] = eval(address)
                api_output = UserOrders(**user_order)
                succes_obj = Success([api_output])
                response = UserOrdersDeserializer(succes_obj)
                return Response({
                    'message': "User data uploaded successfully",
                    'data': response.data['data']
                }, status=status.HTTP_200_OK)
            else:
                message = "Something went wrong"
                data = f"Error: {serializer.errors}"
                failure_ob = Failure(data, 400, message)
                return Response(FailureSerializer(failure_ob).data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = "Internal server Error"
            data = f"Error: {e}"
            failure_ob = Failure(data, 500, message)
            return Response(FailureSerializer(failure_ob).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserOrdersAPI(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user_orders = Orders.objects.filter(
                    user__email=serializer.validated_data['email']
                ).values(
                    'order_id',
                    'order_total',
                    'ordered_date',
                    'delivered_date',
                    'is_paid',
                    order_status=F('order_state__state'),
                    full_name=F('user__full_name'),
                    phone_number=F('user__mobile'),
                    email=F('user__email'),
                    address=F('user__address')
                ).order_by('-order_id')
                if user_orders:
                    for order in user_orders:
                        photos_obj = Photos.objects.filter(order_id=order['order_id'])
                        tile = list(photos_obj.values_list('tile', flat=True).distinct())[0]
                        photos = photos_obj.values_list('photo', flat=True)
                        order.update(photos=list(photos), tile=tile)
                        address = order["address"].replace('null', 'None')
                        order["address"] = eval(address)
                    api_output = []
                    for order in user_orders:
                        output = UserOrders(**order)
                        api_output.append(output)
                    succes_obj = Success(api_output)
                    response = UserOrdersDeserializer(succes_obj)
                    return Response({
                        'status': 200,
                        'message': f"Order details of {user_orders[0]['full_name']}",
                        'data': response.data['data']
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'status': 200,
                        'message': "No orders",
                        'data': f"No orders placed by the user - {serializer.validated_data['email']}"
                    }, status=status.HTTP_200_OK)
            else:
                message = "Something went wrong"
                data = f"Error: {serializer.errors}"
                failure_ob = Failure(data, 400, message)
                return Response(FailureSerializer(failure_ob).data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = "Internal server Error"
            data = f"Error: {e}"
            failure_ob = Failure(data, 500, message)
            return Response(FailureSerializer(failure_ob).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllOrdersAPI(APIView):
    def post(self, request, page=1):
        try:
            orders = Orders.objects.all().order_by('-order_id')[10*(page-1):page*10].values(
                'order_id',
                'order_total',
                'ordered_date',
                'delivered_date',
                'is_paid',
                order_status=F('order_state__state'),
                full_name=F('user__full_name'),
                phone_number=F('user__mobile'),
                email=F('user__email'),
                address=F('user__address')
            )
            for order in orders:
                photos_obj = Photos.objects.filter(order_id=order['order_id'])
                tile = list(photos_obj.values_list('tile', flat=True).distinct())[0]
                photos = photos_obj.values_list('photo', flat=True)
                order.update(photos=list(photos), tile=tile)
                address = order["address"].replace('null', 'None')
                order["address"] = eval(address)
            paginator = Paginator(orders, 10)
            page_obj = paginator.get_page(page)
            api_output = []
            for order in page_obj:
                output = UserOrders(**order)
                api_output.append(output)
            succes_obj = Success(api_output)
            response = UserOrdersDeserializer(succes_obj)
            return Response({
                'status': 200,
                'message': f"Total Order details",
                'data': response.data['data'],
                'count': paginator.count,
                'num_pages': paginator.num_pages
            }, status=status.HTTP_200_OK)
        except Exception as e:
            message = "Internal server Error"
            data = f"Error: {e}"
            failure_ob = Failure(data, 500, message)
            return Response(FailureSerializer(failure_ob).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
