from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя"""
    email = forms.EmailField(required=True)  # email обязателен для заполнения
    username = forms.CharField(required=True, max_length=150)  # username обязателен для заполнения


    class Meta:
        """Мета-класс для настройки формы"""

        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Имя пользователя"})
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Адрес электронной почты"})
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Введите пароль"})
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите пароль повторно"}
        )

    def clean_email(self):
        """Валидация email на уникальность"""
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("Email обязателен для заполнения")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")

        return email


class UserUpdateForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        """Мета-класс для настройки формы"""
        model = User
        fields = ["username", "email", "phone", "avatar", "is_recalled_daily"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Адрес электронной почты"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Номер телефона в формате: +79999999999"}),
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg, image/png, .jpg, .jpeg, .png",
                    "placeholder": "Загрузите изображение в формате jpeg, png, jpg (максимум 5 МБ)",
                }),
            "is_recalled_daily": forms.CheckboxInput(attrs={"class": "form-check-input", "placeholder": "Отметить для ежедневного напоминания о заполнении дневника"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем email readonly, так как он используется для входа
        self.fields["email"].widget.attrs["readonly"] = True

    def clean_avatar(self):
        """Валидация аватара"""
        avatar = self.cleaned_data.get("avatar")

        if not avatar:
            return None

        # Проверка размера файла (максимум 5 МБ)
        max_size = 5 * 1024 * 1024
        if avatar.size > max_size:
            raise forms.ValidationError("Размер файла слишком большой. Максимальный размер: 5 МБ")

        # Проверка формата файла
        valid_extensions = ["jpg", "jpeg", "png"]
        extension = avatar.name.split(".")[-1].lower()

        if extension not in valid_extensions:
            raise forms.ValidationError(f"Неподдерживаемый формат файла. Разрешены: {', '.join(valid_extensions)}")

        return avatar
