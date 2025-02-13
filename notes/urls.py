from django.urls import path

from .views import main_view, authorization_view, registration_view, task_list_view, task_create_view, task_update_view, task_delete_view

urlpatterns = [
    path('', main_view, name='main'),
    path('authorization/', authorization_view, name='authorization'),
    path('registration/', registration_view, name='registration'),
]
