from rest_framework import serializers
from utilities import SuccessSerializer


class AddressSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(allow_null=True)
    mobile = serializers.CharField(allow_null=True)
    address = serializers.CharField(allow_null=True)
    photos = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    tile = serializers.CharField(allow_null=True)
    order_total = serializers.FloatField(allow_null=True)
    is_paid = serializers.BooleanField()


class UserOrders:
    def __init__(
            self,
            order_id: int,
            full_name: str,
            order_total: float,
            ordered_date: str,
            delivered_date: str,
            order_status: str,
            address: str,
            photos: list,
            tile: str,
            is_paid: bool,
            phone_number: str,
            email: str
    ):
        self.order_id = order_id
        self.full_name = full_name
        self.order_total = order_total
        self.ordered_date = ordered_date
        self.delivered_date = delivered_date
        self.order_status = order_status
        self.address = address
        self.photos = photos
        self.tile = tile
        self.is_paid = is_paid
        self.phone_number = phone_number
        self.email = email


class UserOrdersSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    full_name = serializers.CharField(allow_null=True)
    order_total = serializers.FloatField(allow_null=True)
    is_paid = serializers.BooleanField()
    ordered_date = serializers.DateField(allow_null=True)
    delivered_date = serializers.DateField(allow_null=True)
    order_status = serializers.CharField(allow_null=True)
    address = serializers.JSONField(allow_null=True)
    phone_number = serializers.CharField(allow_null=True)
    email = serializers.EmailField(allow_null=True)
    tile = serializers.CharField(allow_null=True)
    photos = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)


class UserOrdersDeserializer(SuccessSerializer):
    data = UserOrdersSerializer(many=True)
