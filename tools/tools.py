"""
Пакет с различными тулзами для приложения
"""
import secrets
from uuid import UUID
from typing import Tuple
from django.http import HttpRequest
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login

from notes.models import Task, CompleteTask


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
    Создание/Возврат словаря сессионных задач
    """
    return request.session.setdefault('session_task', {})


def get_complete_session_task(request: HttpRequest) -> dict:
    """
    Создание/Возврат словаря сессионных завершенных задач
    """
    return request.session.setdefault('complete_session_task', {})


def session_task_transfer(user: User, session_tasks: dict) -> Tuple[bool, list[dict[str: str]]]:
    """
    Перевод незавершенных задач из сессии в бд
    """
    errors = []
    for id_key in session_tasks.keys():
        try:
            task_id = UUID(id_key)
            title = session_tasks.get(id_key, {}).get('title')
            created_at = session_tasks.get(id_key, {}).get('created_at')
            updated_at = session_tasks.get(id_key, {}).get('updated_at')
            is_completed = session_tasks.get(id_key, {}).get('is_completed')

            Task.objects.create(id=task_id,
                                user=user,
                                title=title,
                                created_at=created_at,
                                updated_at=updated_at,
                                is_completed=is_completed)

        except Exception as e:
            errors.append({
                'id': id_key,
                'error': str(e)
            })
        if errors:
            return False, errors
        return True, []


def complete_session_task_transfer(user: User, complete_session_tasks: dict) -> Tuple[bool, list[dict[str: str]]]:
    """
    Перевод завершенных задач из сессии в бд
    """
    errors = []
    for id_key in complete_session_tasks:
        try:
            task_id = UUID(id_key)
            title = complete_session_tasks.get(id_key, {}).get('title')
            created_at = complete_session_tasks.get(id_key, {}).get('created_at')
            updated_at = complete_session_tasks.get(id_key, {}).get('updated_at')
            completed_at = complete_session_tasks.get(id_key, {}).get('completed_at')
            is_completed = complete_session_tasks.get(id_key, {}).get('is_completed')

            CompleteTask.objects.create(id=task_id,
                                        user=user,
                                        title=title,
                                        created_at=created_at,
                                        updated_at=updated_at,
                                        completed_at=completed_at,
                                        is_completed=is_completed)
        except Exception as e:
            errors.append({
                'id': id_key,
                'error': str(e)
            })
        if errors:
            return False, errors
        return True, []


def has_permissions(user, user_obj):
    """
    Проверка прав пользователя
    """
    return user == user_obj
