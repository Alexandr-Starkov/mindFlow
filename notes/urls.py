from django.urls import path

from .views import (main_view, authorization_view, authorization_form_view,
                    registration_view, registration_form_view, logout_view,
                    password_reset_view, password_reset_form_view, password_reset_confirm_view,
                    create_task_view, update_task_view, delete_task_view, update_header_name_view,
                    complete_task_view, incomplete_task_view)


urlpatterns = [
    path('', main_view, name='main'),
    path('create-task/', create_task_view, name='create_task'),
    path('update-task/<uuid:uuid_task_id>', update_task_view, name='update_task'),
    path('delete-task/<uuid:uuid_task_id>', delete_task_view, name='delete_task'),
    path('update-header-name/', update_header_name_view, name='update_header_name'),
    path('complete-task/<uuid:uuid_task_id>', complete_task_view, name='complete_task'),
    path('incomplete-task/<uuid:uuid_task_id>', incomplete_task_view, name='incomplete_task'),
    path('authorization/', authorization_view, name='authorization'),
    path('authorization-form/', authorization_form_view, name='authorization_form'),
    path('registration/', registration_view, name='registration'),
    path('registration-form/', registration_form_view, name='registration_form'),
    path('password-reset/', password_reset_view, name='password_reset'),
    path('password-reset-form/', password_reset_form_view, name='password_reset_form'),
    path('password-reset-confirm/<str:token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('logout/', logout_view, name='logout'),
]
