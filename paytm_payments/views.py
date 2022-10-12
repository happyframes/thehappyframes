import os

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from orders.models import Orders
from paytm_payments.serializers import OrderSerializer
from paytm_payments import Checksum
from loginApp.emails import send_order_successful_email

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


# received_data = dict(request.POST)
#         paytm_params = {}
#         paytm_checksum = received_data['CHECKSUMHASH'][0]
#         for key, value in received_data.items():
#             if key == 'CHECKSUMHASH':
#                 paytm_checksum = value[0]
#             else:
#                 paytm_params[key] = str(value[0])
class HandlePaymentAPI(APIView):
    def post(self, request):
        received_data = dict(request.POST)
        response_dict = {}
        checksum = received_data['CHECKSUMHASH'][0]
        order = None  # initialize the order variable with None

        for key, value in received_data.items():
            # response_dict[i] = form[i]
            if key == 'CHECKSUMHASH':
                # 'CHECKSUMHASH' is coming from paytm and we will assign it to checksum variable to verify our payment
                checksum = value[0]
            else:
                response_dict[key] = str(value[0])

        # we will get an order with id==ORDERID to turn isPaid=True when payment is successful
        order = Orders.objects.get(order_id=received_data['ORDERID'][0])

        # we will verify the payment using our merchant key and the checksum that we are getting from Paytm request.POST
        verify = Checksum.verify_checksum(response_dict, os.getenv('MERCHANTKEY'), checksum)

        if verify:
            if response_dict['RESPCODE'] == '01':
                # if the response code is 01 that means our transaction is successful
                order.isPaid = True
                order.save()
                send_order_successful_email(order.user, received_data['ORDERID'])
                return Response({
                    'status': 200,
                    'message': "Order Successful",
                    'data': response_dict
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 400,
                    'message': f"order was not successful because {response_dict['RESPMSG']}",
                    'data': response_dict
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            received_data['message'] = "Checksum Mismatched"
            return Response({
                    'status': 400,
                    'message': "Checksum Mismatched",
                    'data': response_dict
                }, status=status.HTTP_400_BAD_REQUEST)

