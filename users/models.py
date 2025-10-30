from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=False,  # Не уникальное поле
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите email",
        max_length=254
    )
    phone = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )
############################################################################################
    # Поле для ежедневного напоминания о заполнении дневника
    is_recalled_daily = models.BooleanField(
        default=True,
        verbose_name='Ежедневное напоминание',
        help_text='Отметьте для ежедневного напоминания о заполнении дневника'
    )
############################################################################################
    # Поле для хранения токена временного доступа (для регистрации пользователя)
    token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Токен подтверждения")

    USERNAME_FIELD = "email"  # Обязательное поле для авторизации по email
    REQUIRED_FIELDS = ["username"]  # Обязательные поля для создания суперпользователя (включая email)

    class Meta:
        """Метаданные модели"""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        permissions = [
            ("can_view_user_list", "Может просматривать список пользователей"),
            ("can_block_user", "Может блокировать пользователей"),
        ]

    def __str__(self):
        return f"{self.username} - {self.email}"
