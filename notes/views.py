import json
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

from .models import Task


def main_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'notes/index.html')


def authorization_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'notes/authorization.html')


def authorization_form_view(request: HttpRequest):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_login = data.get('login')
            user_password = data.get('password')

            if not user_login or not user_password:
                return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

            existing_user = is_user_exist(user_login)
            if existing_user:
                user = User.objects.filter(username=user_login).first()

                if not user_password == user.password:
                    return JsonResponse({'error': 'Вы ввели неверный Login или Password'}, status=400)

                user = authenticate(request, username=user_login, password=user_password)
                if user:
                    login(request, user)

                return JsonResponse({
                    'message': 'Успешная авторизация!',
                    'username': user_login,
                    'redirect_url': reverse('main')}, status=200)

            return JsonResponse({'error': 'Пользователя с таким Login не существует!'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные!'}, status=400)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def registration_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'notes/registration.html')


def registration_form_view(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_login = data.get('login')
            user_email = data.get('email')
            user_password = data.get('password')

            if not user_login or not user_email or not user_password:
                return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

            is_create = create_new_user(user_login, user_email, user_password, request)

            if not is_create:
                return JsonResponse({'message': 'Пользователь с таким Login или Email уже существует'}, status=400)

            return JsonResponse({
                'message': f'Успешная регистрация пользователя {user_login}',
                'username': user_login,
                'redirect_url': reverse('main')}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные!'}, status=400)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def create_new_user(*args) -> bool:
    user_login, user_email, user_password, request = args
    try:
        exist = is_user_exist(user_login, user_email)
        if not exist:
            new_user = User.objects.create_user(username=user_login, email=user_email, password=user_password)
            group = Group.objects.get(name='Пользователи приложения')
            new_user.groups.add(group)

            permissions = group.permissions.all()
            new_user.user_permissions.set(permissions)

            if request:
                user = authenticate(request, username=user_login, password=user_password)
                if user:
                    login(request, user)
            return True
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
        return False


def is_user_exist(user_login, user_email=None) -> bool:
    user_by_login = User.objects.filter(username=user_login).first()

    if user_email:
        user_by_email = User.objects.filter(email=user_email).first()
        return user_by_login is not None or user_by_email is not None
    return user_by_login is not None

def logout_view(request: HttpRequest):
    logout(request)
    return redirect('main')


def task_list_view(request: HttpRequest):
    pass


def task_create_view(request: HttpRequest):
    pass


def task_update_view(request: HttpRequest):
    pass


def task_delete_view(request: HttpRequest):
    pass
