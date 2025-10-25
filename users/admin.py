from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Отображаемые поля
    list_display = (
        "id",
        "email",
        "phone",
        "avatar",
        "username",
    )
    # возможность фильтрации
    list_filter = (
        "id",
        "username",
    )
    # возможность поиска по полям
    search_fields = (
        "username",
        "email",
        "phone",
    )
