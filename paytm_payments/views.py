import os
from datetime import datetime 

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from orders.models import Orders
from paytm_payments.serializers import OrderSerializer, OrderStatusSerializer
from paytm_payments import Checksum
from loginApp.emails import send_order_status_email

from dotenv import load_dotenv

load_dotenv()


class StartPaymentAPI(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            order_id = serializer.validated_data['order_id']
            amount = serializer.validated_data['order_total']
            email = serializer.validated_data['email']
            # we have to send the param_dict to the frontend
            # these credentials will be passed to paytm order processor to verify the business account
            param_dict = {
                'MID': os.getenv('MERCHANTID'),
                'ORDER_ID': str(order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'DEFAULT',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'https://thehappyframes.com/payment-status',
                # this is the url of handlepayment function, paytm will send a POST request to the fuction associated with this CALLBACK_URL
            }

            # create new checksum (unique hashed string) using our merchant key with every paytm payment
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, os.getenv('MERCHANTKEY'))
            # send the dictionary with all the credentials to the frontend
            return Response({
                    'status': 200,
                    'message': "Credentials to paytm order processor to verify the business account.",
                    'data': param_dict
                }, status=status.HTTP_200_OK)


class HandlePaymentAPI(APIView):
    def post(self, request):
        try:
            serializer = OrderStatusSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                order_id = serializer.validated_data['order_id']
                order_status = serializer.validated_data['order_status']
                email = serializer.validated_data['email']
                order = Orders.objects.get(order_id=order_id)
    
                if order_status == "Order Processing":
                    order.isPaid = False
                    order.order_state_id = 1
                    order.save()
                    sub = "Order Processing"
                    msg = f"Thank you for shopping with The Happy frames. Your order({order_id}) is processing. " \
                          f"You will receive the order confirmation soon. \n\nThank you, \nThe Happy frames"
                    send_order_status_email(email, sub, msg)
                    return Response({
                        'status': 200,
                        'message': "Order processing email sent to customer",
                        'data': order_status
                    }, status=status.HTTP_200_OK)
                elif order_status == "Order Confirmed":
                    order.isPaid = True
                    order.order_state_id = 2
                    order.save()
                    sub = "Order Confirmed"
                    msg = f"Thank you for shopping with The Happy frames. Your order({order_id}) was successfully " \
                          f"placed and we will deliver your order soon.\n\nThank you, \nThe Happy frames"
                    send_order_status_email(email, sub, msg)
                    return Response({
                        'status': 200,
                        'message': "Order confirmed email sent to customer",
                        'data': order_status
                    }, status=status.HTTP_200_OK)
                elif order_status == "Shipped":
                    order.order_state_id = 3
                    order.save()
                    sub = "Order Shipped"
                    msg = f"Thank you for shopping with The Happy frames. Your order({order_id}) was shipped by the" \
                          f" courier and your order will be delivered soon.\n\nThank you, \nThe Happy frames"
                    send_order_status_email(email, sub, msg)
                    return Response({
                        'status': 200,
                        'message': "Order shipped email sent to customer",
                        'data': order_status
                    }, status=status.HTTP_200_OK)
                elif order_status == "Delivered":
                    order.order_state_id = 4
                    order.save()
                    sub = "Order Delivered"
                    msg = f"Thank you for shopping with The Happy frames. Your order({order_id}) was successfully " \
                          f"delivered on {datetime.today().date()}. We hope you visit us again.\n\nThank you, " \
                          f"\nThe Happy frames"
                    send_order_status_email(email, sub, msg)
                    return Response({
                        'status': 200,
                        'message': "Order delivered email sent to customer",
                        'data': order_status
                    }, status=status.HTTP_200_OK)
                elif order_status == "Cancelled":
                    order.isPaid = False
                    order.order_state_id = 5
                    order.save()
                    sub = "Order Cancelled"
                    msg = f"Thank you for shopping with The Happy frames. Your order({order_id}) was cancelled. " \
                          f"Please be assured, if any amount deducted will be refunded within 5-7 business days." \
                          f"\n\nThank you,\nThe Happy frames"
                    send_order_status_email(email, sub, msg)
                    return Response({
                        'status': 200,
                        'message': "Order cancelled email sent to customer",
                        'data': order_status
                    }, status=status.HTTP_200_OK)
                elif order_status == "Refund initiated":
                    order.order_state_id = 6
                    order.save()
                    sub = "Refund initiated"
                    msg = f"Thank you for shopping with The Happy frames. Refund for your order({order_id}) was " \
                          f"initiated and will be credited to your original payment method within 5-7 business days." \
                          f"\n\nThank you, \nThe Happy frames"
                    send_order_status_email(email, sub, msg)
                    return Response({
                        'status': 200,
                        'message': "Refund initiated email sent to customer",
                        'data': order_status
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'status': 400,
                        'message': "Invalid input",
                        'data': f"Invalid order status - {order_status}"
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 500,
                'message': "Something went wrong",
                'data': f"Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
