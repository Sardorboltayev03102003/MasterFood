from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import User, EmailVerification

from apps.users import models


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255,required=False)
    password = serializers.CharField(max_length=55)
    email = serializers.EmailField(max_length=200)

    model = models.User
    field = ('first_name', 'last_name', 'username', 'password', 'email')
    extra_kwargs = {'password': {'writy_only': True}}

    def validate_email(self, attrs):
        lower_email = attrs.lower()
        if User.objects.filter(email__iexact=lower_email).exists:

            raise serializers.ValidationError("Ushbu email allaqachon mavjud!! ")
        return lower_email

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

        verification = models.EmailVerification.objects.create(user=user)
        verification.generate_code()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.IntegerField(max_value=4)

    def validate(self, attrs):
        verification = EmailVerification.objects.get(code=attrs['code'])

        if verification.expiration_time < now():
            raise serializers.ValidationError("Tasdqilash kodi muddati tugagan!! ")

        attrs['user'] = verification.user

        if verification.code != attrs['code']:
            raise ValidationError("Tasdiqlash kodi noto‘g‘ri.")
