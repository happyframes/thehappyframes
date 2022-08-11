from django.db import models
from django.contrib.auth.models import AbstractUser
from loginApp.manager import UserManager


class UserDetails(AbstractUser):
    username = None
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=4, null=True, blank=True)
    mobile = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email



# class UserDetails(models.Model):
#     user = models.ForeignKey(User, models.CASCADE)
#     full_name = models.CharField(max_length=255, null=True, blank=True)
#     otp = models.CharField(max_length=4, null=True, blank=True)
#     mobile = models.IntegerField(null=True, blank=True)
#     address = models.CharField(max_length=255, null=True, blank=True)
#
#     def __str__(self):
#         return self.full_name
#
#     class Meta:
#         db_table = 'user_details'
