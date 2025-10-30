from django import forms
from my_note.models import Note, NoteImage
# from django.core.exceptions import ValidationError


class NoteImageForm(forms.ModelForm):
    """Форма для загрузки изображений"""
    class Meta:
        model = NoteImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class NoteForm(forms.ModelForm):
    """Форма для создания и редактирования записей"""
    # Поля для загрузки изображений
    image_1 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Изображение 1'
    )
    image_2 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Изображение 2'
    )


    class Meta:
        model = Note
        fields = ['title', 'content', 'is_important']  # поля, которые будут отображаться в форме
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10,}),
            'is_important': forms.CheckboxInput(attrs={"class": "form-check-input",}),
        }
        labels = {
            'title': 'Заголовок заметки',
            'content': 'Содержание заметки',
            'is_important': 'Отметить заметку как важную',
        }

    def clean(self):
        """Проверка размера файлов"""
        cleaned_data = super().clean()
        image_1 = cleaned_data.get('image_1')
        image_2 = cleaned_data.get('image_2')

        # Проверка размера файла (максимум 10 МБ)
        max_size = 10 * 1024 * 1024
        if image_1 and image_1.size > max_size:
            raise forms.ValidationError("Размер файла слишком большой. Максимальный размер: 10 МБ")

        elif image_2 and image_2.size > max_size:
            raise forms.ValidationError("Размер файла слишком большой. Максимальный размер: 10 МБ")

        return cleaned_data

    def save(self, commit=True):
        """Сохранение формы с проверкой на наличие изображений"""
        note = super().save(commit=commit)

        if commit:
            # Сохраняем изображения
            image_1 = self.cleaned_data.get('image_1')
            image_2 = self.cleaned_data.get('image_2')

            # Удаляем старые изображения при редактировании
            if self.instance.pk:
                self.instance.images.all().delete()

            if image_1:
                NoteImage.objects.create(note=note, image=image_1)
            if image_2:
                NoteImage.objects.create(note=note, image=image_2)

        return note


class NoteSearchForm(forms.Form):
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
