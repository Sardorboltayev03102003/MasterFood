from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, EmailVerification

from apps.users import models


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=200, required=False)
    last_name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(max_length=55)


    model = models.User
    field = ('first_name', 'last_name', 'username', 'password', 'email')
    extra_kwargs = {'password': {'writy_only': True}}

    def validate_email(self, value):

        if User.objects.filter(email=value).exists():
            # print(User.objects.filter(email__iexact=lower_email))
            raise serializers.ValidationError("Ushbu email allaqachon mavjud!! ")
        return value

    def validate_username(self, attrs):
        if User.objects.filter(username=attrs).exists():
            raise serializers.ValidationError("Yaratilgan Username band!! ")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.is_email_verify = False
        user.save()

        verification = EmailVerification.objects.create(user=user)
        verification.generate_code()
        return user




def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),  # access_token yaratish
        'refresh_token': str(refresh),  # refresh_token yaratish
    }


class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.IntegerField()

