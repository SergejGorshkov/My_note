from django import forms

from my_note.models import Note


class NoteForm(forms.ModelForm):
    """Форма для создания и редактирования записей"""

    class Meta:
        model = Note
        fields = ['title', 'content', 'image', 'is_important']  # поля, которые будут отображаться в форме
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control', 'placeholder': 'Введите заголовок',
                }),
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control', 'rows': 10, 'placeholder': 'Введите содержание записи',
                }),
            'image': forms.FileInput(attrs={'class': 'form-control',}),
            'is_important': forms.CheckboxInput(attrs={"class": "form-check-input",}),
        }
        labels = {
            'title': 'Заголовок заметки',
            'content': 'Содержание заметки',
            'image': 'Изображение к заметке',
            'is_important': 'Отметить заметку как важную',
        }


class SearchForm(forms.Form):
    """Форма для поиска записей по заголовку или содержанию"""
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по заголовку или содержанию...'
        })
    )

    def clean_query(self):
        """Валидация поискового запроса"""
        query = self.cleaned_data['query']

        # Если запрос пустой, возвращаем как есть
        if not query:
            return query

        query = query.strip()  # Удаление пробелов в начале и конце строки запроса

        # Проверка минимальной длины
        if len(query) < 2:
            raise forms.ValidationError(
                "Запрос должен содержать минимум 2 символа"
            )

        # Проверка максимальной длины строки запроса
        if len(query) > 100:
            raise forms.ValidationError(
                "Запрос не должен превышать 100 символов"
            )

        # Удаление опасных символов для исключения SQL-инъекций
        dangerous_chars = ['\'', '"', ';', '--', '/*', '*/', '<script>', '</script>']
        for char in dangerous_chars:
            query = query.replace(char, '')

        # Нормализация пробелов в запросе
        query = ' '.join(query.split())

        return query