from django.urls import path

from .views import (main_view, authorization_view, authorization_form_view, registration_view, registration_form_view,
                    task_list_view, task_create_view, task_update_view, task_delete_view, logout_view)

urlpatterns = [
    path('', main_view, name='main'),
    path('authorization/', authorization_view, name='authorization'),
    path('authorization-form/', authorization_form_view, name='authorization_form'),
    path('registration/', registration_view, name='registration'),
    path('registration-form/', registration_form_view, name='registration_form'),
    path('logout/', logout_view, name='logout'),
]
