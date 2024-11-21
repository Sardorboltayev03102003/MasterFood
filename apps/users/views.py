import threading
from rest_framework.exceptions import APIException as DRFAPIException
from django.core.mail import send_mail
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from threading import Thread
from django.core.cache import cache
from .models import EmailVerification, generate_code
from .serializers import RegisterSerializer, EmailVerificationSerializer, get_tokens_for_user


class APIException(DRFAPIException):
    status_code = 400
    default_detail = {'detail': 'Something went wrong'}


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        code, exp = generate_code()
        task_1 = threading.Thread(
            target=send_mail,
            kwargs=dict(
                subject='Tasdiqlash kodi',
                message=f"Sizning tasdiqlash kodingiz: {code}\n"
                        f"Kod amal qilish muddati: 10 daqiqa.",
                from_email='your-email@gmail.com',
                recipient_list=[user.email]))

        task_1.start()
        cache.set(f"user_code_{user.id}", code, exp)
        print(code)
        tokens = get_tokens_for_user(user)
        return Response(
            {"detail": "Tasdiqlash kodi emailingizga yuborildi!! ",
             "access_token": tokens['access_token'],
             "refresh_token": tokens['refresh_token']
             },
            status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        user = request.user
        if user.is_email_verify:
            raise APIException("ro'yxatdan o'tkan")
        checking = cache.get(f"user_code_{user.id}")
        if not (checking and checking == code):
            raise APIException("xato")
        user.is_email_verify = True
        user.save()

        return Response({"detail": "Successfull"},
                        status=status.HTTP_400_BAD_REQUEST)
