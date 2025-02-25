import json
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User, Group

from .models import Task


def main_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'notes/index.html')


def authorization_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'notes/authorization.html')


def authorization_form_view(request: HttpRequest):
    pass


def registration_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'notes/registration.html')


def registration_form_view(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            login = data.get('login')
            email = data.get('email')
            password = data.get('password')

            if not login or not email or not password:
                return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

            is_create = create_new_user(login, email, password)

            if not is_create:
                return JsonResponse({'message': 'Пользователь с таким Login или Email уже существует'}, status=400)

            return JsonResponse({
                'message': 'Регистрация успешна!',
                'redirect_url': reverse('main')
                }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные!'}, status=400)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def create_new_user(*args) -> bool:
    login, email, password = args

    try:
        exist = is_user_exist(login, email)
        if not exist:
            new_user = User.objects.create_user(username=login, email=email, password=password)
            group = Group.objects.get(name='Пользователи приложения')
            new_user.groups.add(group)

            permissions = group.permissions.all()
            new_user.user_permissions.set(permissions)

            return True
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
        return False


def is_user_exist(login, email) -> bool:
    user = User.objects.filter(username=login).first()
    if user and user.emal == email:
        return True
    return False


def task_list_view(request: HttpRequest):
    pass


def task_create_view(request: HttpRequest):
    pass


def task_update_view(request: HttpRequest):
    pass


def task_delete_view(request: HttpRequest):
    pass
