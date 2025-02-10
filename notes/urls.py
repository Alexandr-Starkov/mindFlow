from django.urls import path

from .views import task_list_view, task_create_view, task_update_view, task_delete_view

urlpatterns = [
    path('', task_list_view, name='task_list'),
]
