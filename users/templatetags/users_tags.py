# Шаблонный фильтр для медиафайлов.
# Преобразует относительные пути файлов в полные URL-адреса для доступа через медиа-систему Django.

from django import template

# Создается экземпляр Library для регистрации пользовательских шаблонных тегов и фильтров
register = template.Library()


@register.filter()
def media_filter(path):
    """Фильтр будет доступен в шаблонах под именем media_filter"""
    if path:
        return f"/media/{path}" # Если передан путь, возвращает строку вида: "/media/ваш_файл.jpg"
    return "#"
