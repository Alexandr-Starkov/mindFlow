from django.contrib import admin

from .models import Task, PasswordResetToken


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'created_at', 'updated_at', 'is_completed'
    list_display_links = 'pk', 'title'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = 'pk', 'token', 'created_at'
    list_display_links = 'pk', 'token'
