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
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'http://127.0.0.1:8000/paytm_payments/handlepayment/',
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
        checksum = ""
        form = request.data

        response_dict = {}
        order = None  # initialize the order variable with None

        for i in form.keys():
            response_dict[i] = form[i]
            if i == 'CHECKSUMHASH':
                # 'CHECKSUMHASH' is coming from paytm and we will assign it to checksum variable to verify our payment
                checksum = form[i]

            if i == 'ORDERID':
                # we will get an order with id==ORDERID to turn isPaid=True when payment is successful
                order = Orders.objects.get(id=form[i])

        # we will verify the payment using our merchant key and the checksum that we are getting from Paytm request.POST
        verify = Checksum.verify_checksum(response_dict, os.getenv('MERCHANTKEY'), checksum)

        if verify:
            if response_dict['RESPCODE'] == '01':
                # if the response code is 01 that means our transaction is successful
                print('order successful')
                order.isPaid = True
                order.save()
                send_order_successful_email(form['CUSTID'], form['ORDERID'])
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
