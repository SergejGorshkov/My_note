from django.db import models
from config import settings
from django.urls import reverse


class Note(models.Model):
    """Класс для хранения заметок в дневнике"""
    title = models.CharField(
        default='Обычная заметка',
        max_length=255,
        verbose_name='Заголовок заметки'
    )
    content = models.TextField(
        verbose_name='Содержание',
    )
    image = models.ImageField(
        upload_to='my_note/photo',
        blank=True,
        null=True,
        verbose_name='Изображение',
        )
    is_important = models.BooleanField(
        default=False,
        verbose_name='Важная заметка',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания записи'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления записи'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # связь с пользователем, который создал запись (имя - из settings.py)
        on_delete=models.CASCADE,  # если пользователь удален, то поле owner будет очищено
        verbose_name='Автор записи',
        related_name='notes'  # имя поля в модели User для связи с моделью Note
    )

    class Meta:
        """Метаданные модели.
        Порядок сортировки, наименование модели в единственном и множественном числе.
                """
        ordering = ["-is_important", "-created_at"]  # сортировка по важности и по дате создания (сначала новые записи)
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        indexes = ["title", "content"]  # поиск по полям

    def __str__(self):
        return f"self.title - self.created_at"

    def get_absolute_url(self):
        """Возвращает абсолютный URL для детальной страницы заметки"""
        return reverse('note_detail', kwargs={'pk': self.pk})
