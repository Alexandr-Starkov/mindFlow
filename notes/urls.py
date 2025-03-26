from django.urls import path

from .views import (main_view, authorization_view, authorization_form_view,
                    registration_view, registration_form_view, logout_view,
                    password_reset_view, password_reset_form_view, password_reset_confirm_view,
                    create_task_view, update_task_view, delete_task_view, update_title_view)


urlpatterns = [
    path('', main_view, name='main'),
    path('create-task/', create_task_view, name='create_task'),
    path('update_task_view/', update_task_view, name='update_task'),
    path('delete-task/<int:task_id>', delete_task_view, name='delete_task'),
    path('authorization/', authorization_view, name='authorization'),
    path('authorization-form/', authorization_form_view, name='authorization_form'),
    path('registration/', registration_view, name='registration'),
    path('registration-form/', registration_form_view, name='registration_form'),
    path('password-reset/', password_reset_view, name='password_reset'),
    path('password-reset-form/', password_reset_form_view, name='password_reset_form'),
    path('password-reset-confirm/<str:token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('update-title/', update_title_view, name='update_title'),
    path('logout/', logout_view, name='logout'),
]
