from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('my_note.urls', namespace='my_note')),
    path('users/', include('users.urls', namespace='users')),
]

# Динамическое добавление URL-шаблонов для раздачи медиафайлов через Django-сервер в режиме отладки.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
