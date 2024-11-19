from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import User, EmailVerification

from apps.users import models


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        field = ('first_name', 'last_name', 'username', 'password', 'email')
        extra_kwargs = {'password': {'writy_only': True}}

    def validate_email(self, attrs):
        if models.User.objects.filter(email=attrs).exists:
            raise serializers.ValidationError("Ushbu email allaqachon mavjud!! ")
        return attrs

    def validate_username(self, attrs):
        if models.User.objects.filter(username=attrs).exits():
            raise serializers.ValidationError("Yaratilgan Username band!! ")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data('username'),
            email=validated_data('email'),
            password=validated_data('password'),
            first_name=validated_data('first_name'),
            last_name=validated_data('last_name')
        )
        email_verification = models.EmailVerification.objects.create(user=user)
        email_verification.generate_code()  # Assuming this method generates and sets the verification code
        user.email_verify = email_verification  # Link the user with the EmailVerification instance
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.IntegerField(max_value=4)

    def validate(self, attrs):
        verification = EmailVerification.objects.get(code=attrs['code'])

        if verification.expiration_time < now():
            raise serializers.ValidationError("Tasdqilash kodi muddati tugagan!! ")

        attrs['user'] = verification.user
# d
        if verification.code != attrs['code']:
            raise ValidationError("Tasdiqlash kodi noto‘g‘ri.")
