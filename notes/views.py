from django.shortcuts import render
from django.http import HttpRequest

from .models import Task


def main_view(request: HttpRequest):
    return render(request, 'notes/index.html')


def authorization_view(request: HttpRequest):
    return render(request, 'notes/authorization.html')


def registration_view(request: HttpRequest):
    return render(request, 'notes/registration.html')


def task_list_view(request: HttpRequest):
    pass


def task_create_view(request: HttpRequest):
    pass


def task_update_view(request: HttpRequest):
    pass


def task_delete_view(request: HttpRequest):
    pass
