from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
        email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
        email = serializers.EmailField()
        otp = serializers.CharField()
