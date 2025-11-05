from django.urls import path
# from django.views.decorators.cache import cache_page

from my_note.apps import MyNoteConfig
from my_note.views import HomeView, NoteCreateView, NoteDeleteView, NoteDetailView, NoteListView, NoteUpdateView

app_name = MyNoteConfig.name  # Извлечение имени приложения из модуля service_mailing/apps.py

urlpatterns = [
    # Кеширование страницы на 5 минут
    # path('', cache_page(60 * 5)(HomeView.as_view()), name='home'),
    path('', HomeView.as_view(), name='home'),

    path('notes/', NoteListView.as_view(), name='note_list'),
    path('notes/create/', NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note_detail'),
    path('notes/<int:pk>/update/', NoteUpdateView.as_view(), name='note_update'),
    path('notes/<int:pk>/delete/', NoteDeleteView.as_view(), name='note_delete'),
]
