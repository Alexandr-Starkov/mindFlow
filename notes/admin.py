from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'description_short', 'created_at', 'updated_at', 'is_completed'
    list_display_links = 'pk', 'title'

    def description_short(self, obj: Task) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + '...'

    description_short.short_description = 'Short Description'
