from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from loginApp.serializers import RegisterSerializer, VerifyOTPSerializer
from loginApp.emails import send_otp
from loginApp.models import UserDetails
from utilities import Failure, FailureSerializer


class RegisterAPI(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                existing_user = UserDetails.objects.filter(email=serializer.validated_data['email']).exists()
                if not existing_user:
                    user_data = UserDetails.objects.create(
                        email=serializer.validated_data['email']
                    )
                    user_data.save()
                    send_otp(serializer.data['email'])
                else:
                    send_otp(serializer.data['email'])
                return Response({
                    'status': 200,
                    'message': "User data uploaded successfully",
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            message = "Something went wrong"
            data = f"Error: {serializer.errors}"
            failure_ob = Failure(data, 400, message)
            return Response(FailureSerializer(failure_ob).data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = "Internal server Error"
            data = f"Error: {e}"
            failure_ob = Failure(data, 500, message)
            return Response(FailureSerializer(failure_ob).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPAPI(APIView):
    def post(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                saved_otp = UserDetails.objects.filter(email=request.data['email'])[0]
                if serializer.data['otp'] == saved_otp.otp:
                    saved_otp.otp = None
                    saved_otp.save()
                    data = UserDetails.objects.filter(email=serializer.data['email']).values(
                        'email',
                        'full_name',
                        'mobile',
                        'address',
                        'is_staff'
                    )
                    return Response({
                        'status': 200,
                        'message': "OTP matched",
                        'data': data
                    }, status=status.HTTP_200_OK)
                else:
                    message = "Invalid OTP"
                    data = serializer.data
                    failure_ob = Failure(data, 406, message)
                    return Response(FailureSerializer(failure_ob).data, status=status.HTTP_406_NOT_ACCEPTABLE)

            message = "Something went wrong"
            data = f"Error: {serializer.errors}"
            failure_ob = Failure(data, 400, message)
            return Response(FailureSerializer(failure_ob).data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = "Internal server Error"
            data = f"Error: {e}"
            failure_ob = Failure(data, 500, message)
            return Response(FailureSerializer(failure_ob).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

