from django.contrib import admin

from my_note.models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_important', 'created_at',)
    list_filter = ('is_important', 'created_at', 'owner',)
    search_fields = ('title', 'content',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at',)
