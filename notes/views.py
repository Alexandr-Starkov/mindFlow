from django.shortcuts import render
from django.http import HttpRequest

from .models import Task


def task_list_view(request: HttpRequest):
    context = {
        'tasks': Task.objects.all()
    }
    return render(request, 'notes/index.html', context=context)


def task_create_view(request: HttpRequest):
    pass


def task_update_view(request: HttpRequest):
    pass


def task_delete_view(request: HttpRequest):
    pass
