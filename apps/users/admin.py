from django.contrib import admin
from .models import User, EmailVerification
from unfold import admin as u_admin


@admin.register(User)
class UserAdmin(u_admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'password', 'username','is_email_verify')


@admin.register(EmailVerification)
class EmailVerificationAdmin(u_admin.ModelAdmin):
    list_display = ('user','code', 'expiration_time')
# Register your models here.
