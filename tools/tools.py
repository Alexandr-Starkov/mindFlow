"""
Пакет с различными тулзами для приложения
"""
import secrets
from uuid import UUID
from typing import Tuple
from django.http import HttpRequest
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login

from notes.models import Task


def generate_reset_token() -> str:
    """
    Создание токена для восстановления аккаунта
    """
    return secrets.token_urlsafe(32)


def generate_recovery_message(url: str) -> Tuple[str, str, str]:
    """
    Создание шаблон-сообщения для восстановления аккаунта
    """
    subject = 'MindFlow: Password recovery'
    plain_message = f'Follow the link to recover your password: {url}'
    html_message = f'''
<html>
    <body>
        <h1>MindFlow</h1>
        <p>You have requested a password reset. Click the link below to set a new password:</p>
        <a href="{url}">{url}</a>
        <p>If you have not requested password recovery, ignore this email.</p>
    </body>
</html>
'''
    return subject, plain_message, html_message


def create_new_user(*args) -> bool | None:
    """
    Создание нового пользователя
    """
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
        # Реализовать logger
        print(f"Ошибка при создании пользователя: {e}")
        return None
    return False


def is_user_exist(user_login=None, user_email=None) -> User | bool:
    """
    Существует ли пользователь в системе
    """
    user_by_login = User.objects.filter(username=user_login).first()
    user_by_email = User.objects.filter(email=user_email).first()

    if user_by_login:
        return user_by_login
    if user_by_email:
        return user_by_email

    return False


def get_session_task(request: HttpRequest) -> dict:
    """
    Создание/Возврат словаря в пределах сессии для заметок
    """
    return request.session.setdefault('session_task', {})


def session_task_transfer(user: User, session_tasks: dict):
    """
    Перевод заметок из сессии в бд
    """
    for id_key in session_tasks.keys():
        try:
            task_id = UUID(id_key)
            title = session_tasks.get(id_key, {}).get('title')
            is_completed = session_tasks.get(id_key, {}).get('is_completed')
            Task.objects.create(id=task_id, user=user, title=title, is_completed=is_completed)
        except Exception as e:
            print(f"Ошибка при создании task'a в session_task_transfer: {e}")
            return
