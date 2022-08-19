from rest_framework import serializers


class OrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_total = serializers.FloatField()
    email = serializers.EmailField()
