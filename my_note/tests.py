from users.models import User

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from my_note.models import Note, NoteImage
from my_note.forms import NoteForm, NoteSearchForm, NoteImageForm


class NoteModelTest(TestCase):
    """Тесты модели Note"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.note = Note.objects.create(
            title='Test Note',
            content='This is a test note content',
            owner=self.user
        )

    def test_note_creation(self):
        """Тест создания заметки"""
        self.assertEqual(self.note.title, 'Test Note')
        self.assertEqual(self.note.content, 'This is a test note content')
        self.assertEqual(self.note.owner, self.user)
        self.assertFalse(self.note.is_important)
        self.assertIsNotNone(self.note.created_at)
        self.assertIsNotNone(self.note.updated_at)

    def test_note_str_representation(self):
        """Тест строкового представления заметки"""
        self.assertIn('Test Note', str(self.note))
        self.assertIn(str(self.note.created_at.date()), str(self.note))


class NoteImageModelTest(TestCase):
    """Тесты модели NoteImage"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.note = Note.objects.create(
            title='Test Note with Image',
            content='This note has images',
            owner=self.user
        )

    def test_note_image_creation(self):
        """Тест создания изображения для заметки"""
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        note_image = NoteImage.objects.create(
            note=self.note,
            image=image_file
        )
        self.assertEqual(note_image.note, self.note)
        self.assertIsNotNone(note_image.image)
        self.assertIsNotNone(note_image.created_at)

    def test_note_image_str_representation(self):
        """Тест строкового представления изображения"""
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        note_image = NoteImage.objects.create(
            note=self.note,
            image=image_file
        )
        self.assertIn('Изображение для', str(note_image))
        self.assertIn(self.note.title, str(note_image))


class HomeViewTest(TestCase):
    """Тесты домашней страницы"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.home_url = reverse('my_note:home')

    def test_home_view_unauthenticated(self):
        """Тест домашней страницы для неаутентифицированного пользователя"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_note/home.html')
        self.assertEqual(len(response.context['recent_notes']), 0)
        self.assertEqual(response.context['total_notes'], 0)

    def test_home_view_authenticated(self):
        """Тест домашней страницы для аутентифицированного пользователя"""
        # Создаем заметки для пользователя
        for i in range(7):
            Note.objects.create(
                title=f'Note {i}',
                content=f'Content {i}',
                owner=self.user
            )

        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.home_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_note/home.html')
        # Должны отображаться только последние 5 заметок
        self.assertEqual(len(response.context['recent_notes']), 5)
        self.assertEqual(response.context['total_notes'], 7)


class NoteListViewTest(TestCase):
    """Тесты списка заметок"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.note_list_url = reverse('my_note:note_list')

        # Создаем заметки для тестового пользователя
        for i in range(12):
            Note.objects.create(
                title=f'User Note {i}',
                content=f'User Content {i}',
                owner=self.user
            )

        # Создаем заметки для другого пользователя
        for i in range(3):
            Note.objects.create(
                title=f'Other User Note {i}',
                content=f'Other User Content {i}',
                owner=self.other_user
            )

    def test_note_list_unauthenticated(self):
        """Тест списка заметок для неаутентифицированного пользователя"""
        response = self.client.get(self.note_list_url)
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_note_list_authenticated(self):
        """Тест списка заметок для аутентифицированного пользователя"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.note_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_note/note_list.html')
        # Должны видеть только свои заметки
        self.assertEqual(len(response.context['notes']), 10)  # paginate_by = 10
        self.assertEqual(response.context['paginator'].count, 12)  # Всего заметок пользователя

    def test_note_list_search(self):
        """Тест поиска в списке заметок"""
        self.client.login(email='test@example.com', password='testpass123')

        # Создаем заметку с уникальным содержимым для поиска
        Note.objects.create(
            title='Unique Search Note',
            content='This is a unique content for search',
            owner=self.user
        )

        response = self.client.get(self.note_list_url, {'query': 'unique'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notes']), 1)
        self.assertEqual(response.context['notes'][0].title, 'Unique Search Note')

    def test_note_list_pagination(self):
        """Тест пагинации списка заметок"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.note_list_url + '?page=2')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notes']), 2)  # На второй странице 2 заметки из 12


class NoteDetailViewTest(TestCase):
    """Тесты детальной страницы заметки"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.note = Note.objects.create(
            title='Test Note',
            content='Test Content',
            owner=self.user
        )
        self.note_detail_url = reverse('my_note:note_detail', kwargs={'pk': self.note.pk})

    def test_note_detail_authenticated_owner(self):
        """Тест детальной страницы для владельца заметки"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.note_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_note/note_detail.html')
        self.assertEqual(response.context['note'], self.note)

    def test_note_detail_authenticated_other_user(self):
        """Тест детальной страницы для другого пользователя"""
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(self.note_detail_url)

        self.assertEqual(response.status_code, 404)  # Не должен видеть чужие заметки

    def test_note_detail_unauthenticated(self):
        """Тест детальной страницы для неаутентифицированного пользователя"""
        response = self.client.get(self.note_detail_url)
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа


class NoteCreateViewTest(TestCase):
    """Тесты создания заметки"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.note_create_url = reverse('my_note:note_create')

    def test_note_create_unauthenticated(self):
        """Тест создания заметки неаутентифицированным пользователем"""
        response = self.client.get(self.note_create_url)
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_note_create_get_authenticated(self):
        """Тест GET запроса для создания заметки"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.note_create_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_note/note_form.html')
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_create_post_valid(self):
        """Тест POST запроса с валидными данными"""
        self.client.login(email='test@example.com', password='testpass123')

        form_data = {
            'title': 'New Test Note',
            'content': 'This is new test content',
            'is_important': True,
        }

        response = self.client.post(self.note_create_url, form_data)

        # Проверяем редирект на список заметок
        self.assertRedirects(response, reverse('my_note:note_list'))

        # Проверяем создание заметки
        note = Note.objects.get(title='New Test Note')
        self.assertEqual(note.content, 'This is new test content')
        self.assertEqual(note.owner, self.user)
        self.assertTrue(note.is_important)


class NoteUpdateViewTest(TestCase):
    """Тесты обновления заметки"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.note = Note.objects.create(
            title='Original Note',
            content='Original Content',
            owner=self.user
        )
        self.note_update_url = reverse('my_note:note_update', kwargs={'pk': self.note.pk})

    def test_note_update_authenticated_owner(self):
        """Тест обновления заметки владельцем"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.note_update_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_note/note_form.html')
        self.assertEqual(response.context['object'], self.note)

    def test_note_update_authenticated_other_user(self):
        """Тест обновления заметки другим пользователем"""
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(self.note_update_url)

        self.assertEqual(response.status_code, 404)  # Не должен иметь доступа

    def test_note_update_post_valid(self):
        """Тест POST запроса на обновление заметки"""
        self.client.login(email='test@example.com', password='testpass123')

        form_data = {
            'title': 'Updated Note',
            'content': 'Updated Content',
            'is_important': True,
        }

        response = self.client.post(self.note_update_url, form_data)

        self.assertRedirects(response, reverse('my_note:note_list'))

        # Проверяем обновление заметки
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')
        self.assertEqual(self.note.content, 'Updated Content')
        self.assertTrue(self.note.is_important)


class NoteDeleteViewTest(TestCase):
    """Тесты удаления заметки"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.note = Note.objects.create(
            title='Note to Delete',
            content='This note will be deleted',
            owner=self.user
        )
        self.note_delete_url = reverse('my_note:note_delete', kwargs={'pk': self.note.pk})

    def test_note_delete_authenticated_owner(self):
        """Тест удаления заметки владельцем"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.note_delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_note/note_confirm_delete.html')
        self.assertEqual(response.context['note'], self.note)

    def test_note_delete_authenticated_other_user(self):
        """Тест удаления заметки другим пользователем"""
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(self.note_delete_url)

        self.assertEqual(response.status_code, 404)  # Не должен иметь доступа

    def test_note_delete_post(self):
        """Тест POST запроса на удаление заметки"""
        self.client.login(email='test@example.com', password='testpass123')

        response = self.client.post(self.note_delete_url)

        self.assertRedirects(response, reverse('my_note:note_list'))

        # Проверяем, что заметка удалена
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())


class IntegrationTest(TestCase):
    """Интеграционные тесты полного цикла работы с заметками"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_complete_note_workflow(self):
        """Тест полного цикла создания, редактирования и удаления заметки"""
        self.client.login(email='test@example.com', password='testpass123')

        # 1. Создание заметки
        create_data = {
            'title': 'Integration Test Note',
            'content': 'This is integration test content',
            'is_important': True,
        }
        response = self.client.post(reverse('my_note:note_create'), create_data)
        self.assertRedirects(response, reverse('my_note:note_list'))

        note = Note.objects.get(title='Integration Test Note')
        self.assertEqual(note.content, 'This is integration test content')
        self.assertTrue(note.is_important)

        # 2. Просмотр списка заметок
        response = self.client.get(reverse('my_note:note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(note, response.context['notes'])

        # 3. Просмотр детальной страницы
        response = self.client.get(reverse('my_note:note_detail', kwargs={'pk': note.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['note'], note)

        # 4. Редактирование заметки
        update_data = {
            'title': 'Updated Integration Note',
            'content': 'Updated integration content',
            'is_important': False,
        }
        response = self.client.post(
            reverse('my_note:note_update', kwargs={'pk': note.pk}),
            update_data
        )
        self.assertRedirects(response, reverse('my_note:note_list'))

        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated Integration Note')
        self.assertEqual(note.content, 'Updated integration content')
        self.assertFalse(note.is_important)

        # 5. Удаление заметки
        response = self.client.post(reverse('my_note:note_delete', kwargs={'pk': note.pk}))
        self.assertRedirects(response, reverse('my_note:note_list'))
        self.assertFalse(Note.objects.filter(pk=note.pk).exists())
