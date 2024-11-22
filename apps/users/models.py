import datetime
import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.models import BaseModel


class User(AbstractUser):
    is_email_verify = models.BooleanField(default=False)
    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'


class EmailVerification(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_verify")
    code = models.CharField(max_length=4)
    expiration_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expiration_time:
            self.expiration_time = now() + datetime.timedelta(minutes=10)
        super().save(*args, **kwargs)


def generate_code():
    code = str(random.randint(1000, 9999))
    return code, 120
