from django.contrib import admin

from .models import Task, CompleteTask, PasswordResetToken, HeaderTitle


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = 'pk', 'user', 'title', 'created_at', 'updated_at', 'is_completed'
    list_display_links = 'pk', 'user', 'title'


@admin.register(CompleteTask)
class CompleteTaskAdmin(admin.ModelAdmin):
    list_display = 'pk', 'user', 'title', 'created_at', 'updated_at', 'completed_at', 'is_completed'
    list_display_links = 'pk', 'user', 'title'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = 'pk', 'token', 'created_at'
    list_display_links = 'pk', 'token'


@admin.register(HeaderTitle)
class HeaderTitleAdmin(admin.ModelAdmin):
    list_display = 'pk', 'user', 'header_title'
    list_display_links = 'pk', 'user'
