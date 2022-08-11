from django.db import models
from loginApp.models import UserDetails


class OrderState(models.Model):
    order_state_id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=255)

    class Meta:
        db_table = 'order_state'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserDetails, models.DO_NOTHING)
    order_total = models.FloatField()
    is_paid = models.BooleanField()
    ordered_date = models.DateField(auto_now_add=True)
    delivered_date = models.DateField(null=True, blank=True)
    order_state = models.ForeignKey(OrderState, models.DO_NOTHING, null=True, blank=True)

    class Meta:
        db_table = 'orders'


class Photos(models.Model):
    photo_url = models.URLField(null=True, blank=True)
    tile_url = models.URLField(null=True, blank=True)
    order = models.ForeignKey(Orders, models.CASCADE)

    class Meta:
        db_table = 'photos'
