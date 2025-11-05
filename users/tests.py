from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CustomUserCreationForm, UserUpdateForm
from users.models import User


class UserModelTest(TestCase):
    """Тесты модели User"""

    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_active=False  # По умолчанию не активен до подтверждения email
        )
        self.user.set_password('testpass123')
        self.user.save()

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_active)  # По умолчанию не активен до подтверждения email

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(str(self.user), 'testuser - test@example.com')

    def test_user_fields(self):
        """Тест дополнительных полей пользователя"""
        self.user.tg_chat_id = '123456789'
        self.user.phone = '+79991234567'
        self.user.is_recalled_daily = True
        self.user.token = 'test_token'
        self.user.save()

        updated_user = User.objects.get(email='test@example.com')
        self.assertEqual(updated_user.tg_chat_id, '123456789')
        self.assertEqual(updated_user.phone, '+79991234567')
        self.assertTrue(updated_user.is_recalled_daily)
        self.assertEqual(updated_user.token, 'test_token')

    def test_unique_email_constraint(self):
        """Тест уникальности email"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                username='anotheruser',
                password='testpass123'
            )


class CustomUserCreationFormTest(TestCase):
    """Тесты формы регистрации"""

    def test_valid_form(self):
        """Тест валидной формы"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_duplicate_email(self):
        """Тест формы с дублирующимся email"""
        User.objects.create_user(
            email='existing@example.com',
            username='existinguser',
            password='testpass123'
        )

        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_form_password_mismatch(self):
        """Тест формы с несовпадающими паролями"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_validation_empty_email(self):
        """Тест валидации пустого email"""
        form_data = {
            'username': 'newuser',
            'email': '',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class UserUpdateFormTest(TestCase):
    """Тесты формы редактирования профиля"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_active=True
        )

    def test_valid_form(self):
        """Тест валидной формы редактирования"""
        form_data = {
            'username': 'updateduser',
            'email': 'test@example.com',  # email остается тем же
            'tg_chat_id': '123456789',
            'phone': '+79991234567',
            'is_recalled_daily': True,
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_email_field_readonly(self):
        """Тест, что поле email только для чтения"""
        form = UserUpdateForm(instance=self.user)
        self.assertTrue(form.fields['email'].widget.attrs.get('readonly'))


class RegisterViewTest(TestCase):
    """Тесты представления регистрации"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }

    def test_register_view_get(self):
        """Тест GET запроса к странице регистрации"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_view_post_valid(self):
        """Тест POST запроса с валидными данными"""
        response = self.client.post(self.register_url, self.valid_data)

        # Проверяем редирект на страницу входа
        self.assertRedirects(response, reverse('users:login'))

        # Проверяем создание пользователя
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertFalse(user.is_active)  # Пользователь не активен до подтверждения email
        self.assertIsNotNone(user.token)  # Токен должен быть установлен

        # Проверяем отправку email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Подтверждение email для регистрации')

    def test_register_view_post_invalid(self):
        """Тест POST запроса с невалидными данными"""
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'differentpassword'

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertFalse(User.objects.filter(email='newuser@example.com').exists())


class EmailVerificationTest(TestCase):
    """Тесты подтверждения email"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_active=False,
            token='test_token_123'
        )

    def test_email_verification_success(self):
        """Тест успешного подтверждения email"""
        verification_url = reverse('users:email-confirm', kwargs={'token': 'test_token_123'})
        response = self.client.get(verification_url)

        # Проверяем редирект
        self.assertRedirects(response, reverse('users:login'))

        # Проверяем активацию пользователя
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.is_active)

    def test_email_verification_invalid_token(self):
        """Тест подтверждения email с неверным токеном"""
        verification_url = reverse('users:email-confirm', kwargs={'token': 'invalid_token'})
        response = self.client.get(verification_url)

        self.assertEqual(response.status_code, 404)  # Должен вернуть 404


class UserProfileViewTest(TestCase):
    """Тесты просмотра профиля"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_active=True
        )
        self.profile_url = reverse('users:profile')

    def test_profile_view_authenticated(self):
        """Тест просмотра профиля аутентифицированным пользователем"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['user_profile'], self.user)

    def test_profile_view_unauthenticated(self):
        """Тест просмотра профиля неаутентифицированным пользователем"""
        response = self.client.get(self.profile_url)

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)


class UserProfileUpdateViewTest(TestCase):
    """Тесты редактирования профиля"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_active=True
        )
        self.profile_edit_url = reverse('users:profile_edit')

    def test_profile_edit_view_authenticated_get(self):
        """Тест GET запроса к редактированию профиля аутентифицированным пользователем"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.profile_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')
        self.assertIsInstance(response.context['form'], UserUpdateForm)
        self.assertEqual(response.context['object'], self.user)

    def test_profile_edit_view_authenticated_post_valid(self):
        """Тест POST запроса с валидными данными"""
        self.client.login(email='test@example.com', password='testpass123')

        updated_data = {
            'username': 'updateduser',
            'email': 'test@example.com',  # email не меняется
            'tg_chat_id': '123456789',
            'phone': '+79991234567',
            'is_recalled_daily': True,
        }

        response = self.client.post(self.profile_edit_url, updated_data)

        # Проверяем редирект на профиль
        self.assertRedirects(response, reverse('users:profile'))

        # Проверяем обновление данных
        updated_user = User.objects.get(email='test@example.com')
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertEqual(updated_user.tg_chat_id, '123456789')
        self.assertEqual(updated_user.phone, '+79991234567')
        self.assertTrue(updated_user.is_recalled_daily)

    def test_profile_edit_view_unauthenticated(self):
        """Тест редактирования профиля неаутентифицированным пользователем"""
        response = self.client.get(self.profile_edit_url)

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)
