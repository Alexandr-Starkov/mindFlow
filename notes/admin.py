from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'created_at', 'updated_at', 'is_completed'
    list_display_links = 'pk', 'title'
