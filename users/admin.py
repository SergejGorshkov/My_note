from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'tg_chat_id', 'phone', 'is_recalled_daily']
    list_filter = ['username', 'is_recalled_daily', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'phone', 'tg_chat_id']

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'avatar', 'is_recalled_daily', 'token', 'tg_chat_id')
        }),
    )
