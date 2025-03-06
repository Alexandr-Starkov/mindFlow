import json
import secrets
from typing import Tuple
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from .models import Task, PasswordResetToken


def generate_reset_token():
    return secrets.token_urlsafe(32)


def generate_data_message(url: str) -> Tuple[str, str, str]:
    subject = 'MindFlow: Password recovery'
    plain_message = f'Follow the link to recover your password: {url}'
    html_message = f'''
<html>
    <body>
        <h1>MindFlow</h1>
        <p>You have requested a password reset. Click the link below to set a new password:</p>
        <a href="{url}">Restore password</a>
        <p>If you have not requested password recovery, ignore this email.</p>
    </body>
</html>
'''
    return subject, plain_message, html_message


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

            user = authenticate(request, username=user_login, password=user_password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'message': 'Успешная авторизация!',
                    'username': user_login,
                    'redirect_url': reverse('main')
                }, status=200)
            else:
                return JsonResponse({'error': 'Вы ввели неверный Login или Password!'}, status=400)
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
    return False


def is_user_exist(user_login=None, user_email=None) -> User | bool:
    if user_login:
        user_by_login = User.objects.filter(username=user_login).first()
        if user_by_login:
            return user_by_login

    if user_email:
        user_by_email = User.objects.filter(email=user_email).first()
        if user_by_email:
            return user_by_email

    return False


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('main')


def password_reset_view(request: HttpRequest):
    return render(request, 'notes/password-reset.html')


def password_reset_form_view(request: HttpRequest):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_email = data.get('email')
            if not user_email:
                return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

            user = is_user_exist(user_email=user_email)
            if not user:
                return JsonResponse({'error': 'Пользователя с введенным email несуществует'}, status=400)

            # Token Generation
            token = generate_reset_token()
            # Token Save in Data Base
            PasswordResetToken.objects.create(user=user, token=token)
            # Send email with token
            reset_url = request.build_absolute_uri(reverse('password_reset_confirm', args=[token]))
            subject, plain_message, html_message = generate_data_message(reset_url)

            send_mail(
                subject,
                plain_message,
                settings.EMAIL_HOST_USER,
                [user_email],
                fail_silently=False,
                html_message=html_message,
            )

            return JsonResponse({
                'instruction_message': 'Письмо с инструкциями отправлено на ваш email',
                'redirect_url': reverse('main'),
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные!'}, status=400)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def password_reset_confirm_view(request: HttpRequest, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_password = data.get('new_password')
        password_confirm = data.get('password_confirm')

        if not new_password or not password_confirm:
            return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

        if new_password != password_confirm:
            return JsonResponse({'error': 'Пароли не сопвадают'}, status=400)

        reset_token = PasswordResetToken.objects.filter(token=token).first()
        if not reset_token:
            return JsonResponse({'error': 'Недействительный токен'}, status=400)

        # Check token time
        if reset_token.created_at < timezone.now() - timedelta(hours=1):
            return JsonResponse({'error': 'Срок действия токена истек'}, status=400)

        # Update password
        user = reset_token.user
        user.password = make_password(new_password)
        user.save()

        reset_token.delete()

        return JsonResponse({
            'instruction_message': 'Пароль успешно изменен!',
            'redirect_url': reverse('main'),
        }, status=200)

    return render(request, 'notes/password_reset_confirm.html', {'token': token})


def task_list_view(request: HttpRequest):
    pass


def task_create_view(request: HttpRequest):
    pass


def task_update_view(request: HttpRequest):
    pass


def task_delete_view(request: HttpRequest):
    pass
