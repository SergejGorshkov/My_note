from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from django.db.models import Q  # Библиотека для поиска по запросу в БД

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from my_note.models import Note
from my_note.forms import NoteForm, NoteSearchForm
from django.urls import reverse_lazy


class HomeView(ListView):
    """ Класс для отображения домашней страницы """
    template_name = 'my_note/home.html'
    context_object_name = 'recent_notes'  # Имя переменной в шаблоне

    def get_queryset(self):
        """ Получение своих последних 5 заметок на главной странице """
        if self.request.user.is_authenticated:
            return Note.objects.filter(owner=self.request.user)[:5]
        return Note.objects.none()

    def get_context_data(self, **kwargs):
        """ Добавление количества заметок в контекст """
        context = super().get_context_data(**kwargs)
        context['total_notes'] = Note.objects.filter(
            owner=self.request.user).count() if self.request.user.is_authenticated else 0
        return context


class NoteListView(LoginRequiredMixin, ListView):
    """ Класс для отображения списка заметок """
    model = Note
    template_name = 'my_note/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        """ Фильтрация заметок по пользователю """
        queryset = Note.objects.filter(owner=self.request.user)

        # Поиск по запросу в БД
        search_form = NoteSearchForm(self.request.GET)  # Создаем форму из GET-запроса
        # Если форма валидна и есть запрос в форме...
        if search_form.is_valid() and search_form.cleaned_data['query']:
            query = search_form.cleaned_data['query']
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """ Добавление формы поиска в контекст """
        # Получение контекста родительского класса
        context = super().get_context_data(**kwargs)
        context['search_form'] = NoteSearchForm(self.request.GET)
        return context


class NoteDetailView(LoginRequiredMixin, DetailView):
    """ Класс для отображения детальной информации о заметке """
    model = Note
    template_name = 'my_note/note_detail.html'
    context_object_name = 'note'  # Имя переменной в шаблоне

    def get_queryset(self):
        """ Фильтрация заметок по пользователю """
        return Note.objects.filter(owner=self.request.user)


class NoteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """ Класс для создания заметки """
    model = Note
    form_class = NoteForm
    template_name = 'my_note/note_form.html'
    success_message = "Заметка успешно создана!"
    success_url = reverse_lazy("my_note:note_list")

    def form_valid(self, form):
        """ Переопределение метода для сохранения заметки """
        form.instance.owner = self.request.user  # Добавление владельца заметки
        return super().form_valid(form)


class NoteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """ Класс для обновления заметки """
    model = Note
    form_class = NoteForm
    template_name = 'my_note/note_form.html'
    success_message = "Заметка успешно обновлена!"
    success_url = reverse_lazy("my_note:note_list")

    def get_queryset(self):
        """ Фильтрация заметок по пользователю """
        return Note.objects.filter(owner=self.request.user)

    def get_initial(self):
        initial = super().get_initial()  # Получаем начальные данные формы
        # Заполняем поля изображений при редактировании
        images = self.object.images.all()  # Получаем все изображения заметки
        if images:
            for i, image in enumerate(images[:2], 1):  # Добавляем первые 2 изображения
                initial[f'image_{i}'] = image.image  # Добавляем поле изображения к начальным данным
        return initial


class NoteDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """ Класс для удаления заметки """
    model = Note
    context_object_name = 'note'  # Имя переменной в шаблоне
    template_name = 'my_note/note_confirm_delete.html'
    success_url = reverse_lazy("my_note:note_list")
    success_message = "Заметка успешно удалена!"

    def get_queryset(self):
        """ Фильтрация заметок по пользователю """
        return Note.objects.filter(owner=self.request.user)
