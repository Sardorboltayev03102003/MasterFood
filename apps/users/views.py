import random

from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import Token

from .serializers import RegisterSerializer, EmailVerificationSerializer
from .models import User, EmailVerification
from rest_framework import generics


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        code = str(random.randint(1000, 9999))
        verification = EmailVerification.objects.create(user=user, code=code)
        send_mail(
            subject='Tasdiqlash kodi',
            message=f"Sizning tasdiqlash kodingiz: {verification.code}\n"
                    f"Kod amal qilish muddati: 10 daqiqa.",
            from_email='your-email@gmail.com',
            recipient_list=[user.email]
        )
        return Response({"detail": "Tasdiqlash kodi emailingizga yuborildi!! "},
                        status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        try:
            # Tasdiqlash kodiga ega foydalanuvchini qidiring
            verification = EmailVerification.objects.get(code=code)

            # Kod muddati tugaganligini tekshirish
            if verification.expiration_time < now():
                return Response({"detail": "Tasdiqlash kodi muddati tugagan."},
                                status=status.HTTP_400_BAD_REQUEST)

            user = verification.user
            user.email_verified = True
            user.save()

            # Tasdiqlash kodini o‘chirish (ixtiyoriy)
            # verification.delete()

            # Token yaratish
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"detail": "Email muvaffaqiyatli tasdiqlandi.", "token": token.key},
                            status=status.HTTP_200_OK)

        except EmailVerification.DoesNotExist:
            return Response({"detail": "Tasdiqlash kodi noto‘g‘ri."},
                            status=status.HTTP_400_BAD_REQUEST)
