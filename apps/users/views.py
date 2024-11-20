import random

from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import Token

from .serializers import RegisterSerializer, EmailVerificationSerializer,get_tokens_for_user
from .models import User, EmailVerification
from rest_framework import generics

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # code = str(random.randint(1000, 9999))
        verification, created = EmailVerification.objects.get_or_create(user=user)

        if created:
            verification.generate_code()
        else:
            verification.generate_code()
        send_mail(
            subject='Tasdiqlash kodi',
            message=f"Sizning tasdiqlash kodingiz: {verification.code}\n"
                    f"Kod amal qilish muddati: 10 daqiqa.",
            from_email='your-email@gmail.com',
            recipient_list=[user.email]
        )
        tokens = get_tokens_for_user(user)
        return Response(
            {"detail": "Tasdiqlash kodi emailingizga yuborildi!! ",
             "access_token": tokens['access_token'],
             "refresh_token": tokens['refresh_token']
             },
            status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

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
            return Response({"detail": "Email muvaffaqiyatli tasdiqlandi."},
                            status=status.HTTP_200_OK)

        except EmailVerification.DoesNotExist:
            return Response({"detail": "Tasdiqlash kodi noto‘g‘ri."},
                            status=status.HTTP_400_BAD_REQUEST)
