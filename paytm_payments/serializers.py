from rest_framework import serializers


class OrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_total = serializers.FloatField()
    email = serializers.EmailField()


class OrderStatusSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_status = serializers.CharField(max_length=50)
    email = serializers.EmailField()
