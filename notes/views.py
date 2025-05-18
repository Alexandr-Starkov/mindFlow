import json
import uuid
from typing import Union
from datetime import timedelta, date
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.db import IntegrityError

from .models import Task, CompleteTask, PasswordResetToken, HeaderTitle
from tools.tools import (get_session_task, get_complete_session_task, session_task_transfer, complete_session_task_transfer,
                         generate_reset_token, generate_recovery_message, create_new_user, is_user_exist, has_permissions)


def main_view(request: HttpRequest) -> HttpResponse | JsonResponse:
    if request.method == 'GET':
        user_header_title = None
        session_task = get_session_task(request)
        complete_session_task = get_complete_session_task(request)
        if request.user.is_authenticated:
            print(f'Пришел GET запрос в main_view от авторизованного пользователя - {request.user}')
            user = request.user

            # Перенос сессионных незавершенных задач, при наличии
            if session_task:
                result, errors = session_task_transfer(user, session_task)
                if errors:
                    # Логгер
                    for err in errors:
                        print(f"Ошибка при переносе сессионных незавершенных задач {err['id']}: {err['error']}")
                else:
                    del request.session['session_task']

            tasks = Task.objects.filter(user=user).order_by('-created_at')

            # Перенос сессионных завершенных задач, при наличии
            if complete_session_task:
                result, errors = complete_session_task_transfer(user, complete_session_task)
                if errors:
                    # Логер
                    for err in errors:
                        print(f"Ошибка при переносе сессионных заверешенных задач {err['id']}: {err['error']}")
                else:
                    del request.session['complete_session_task']

            complete_tasks = CompleteTask.objects.filter(user=user).order_by('-completed_at')

            # Подтягиваем заголовок пользователя
            header_obj = HeaderTitle.objects.filter(user=user).first()
            user_header_title = header_obj.header_title if header_obj else None
        else:
            print('Пришел GET запрос в main_view от неавторизованного пользователя')
            # Подготовка и сортировка незавершенных сессионных задач
            session_task_sorted = sorted(
                session_task.items(),
                key=lambda item: item[1]['created_at'],
                reverse=True
            )
            tasks = [{'id': key, **value} for key, value in session_task_sorted]

            # Подготовка и сортировка завершенных сессионных задач
            complete_session_task_sorted = sorted(
                complete_session_task.items(),
                key=lambda item: item[1]['completed_at'],
                reverse=True
            )
            complete_tasks = [{'id': key, **value} for key, value in complete_session_task_sorted]

        context = {
            'tasks': tasks,
            'complete_tasks': complete_tasks,
            'user_header_title': user_header_title,
            'date': date.today().strftime('%d/%m/%Y'),
        }

        response = render(request, 'notes/index.html', context=context)
        # Заголовки против кеширования
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return JsonResponse({'error': 'Только GET запросы!'}, status=405)


def update_header_name_view(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        print('Пришел POST запрос в update_header_name_view на обновление заголовка')
        try:
            data = json.loads(request.body)
            new_header_name = data.get('newHeaderName')
            if not new_header_name:
                return JsonResponse({'error': 'Новое имя заголовка не может быть пустым!'}, status=403)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Ошибка формата JSON'}, status=400)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Неавторизованный пользователь
        if not request.user.is_authenticated:
            request.session['new_header_name'] = new_header_name
            return JsonResponse({'message': f'Header-Title успешно изменен на {new_header_name}',
                                 'new_header_name': new_header_name}, status=200)

        # Авторизованный пользователь
        header_obj, created = HeaderTitle.objects.get_or_create(user=request.user)
        # Проверка прав на изменение заголовка
        if not has_permissions(request.user, header_obj.user):
            return JsonResponse({'error': 'Доступ заперещен!'}, status=403)

        header_obj.header_title = new_header_name
        header_obj.save()

        return JsonResponse({
            'message': f"Header-Title успешно {'создан' if created else 'обновлен'} на {new_header_name}",
            'new_header_name': header_obj.header_title,
        }, status=200)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def create_task_view(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_task = data.get('newTask')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные!'}, status=400)

        if not new_task:
            return JsonResponse({'error': 'Заполните значение для задачи, название не должно быть пустым!'},
                                status=400)

        # Авторизованные пользователь
        if request.user.is_authenticated:
            print(f'Пришел POST запрос в create_task_view на добавление новой задачи от авторизованного пользователя {request.user}')
            user = request.user

            # Перевод незаконченных задач из сессии в бд
            session_task = get_session_task(request)
            if session_task:
                session_task_transfer(user, session_task)
                # Очищаем незаконченные задачи из сессии
                del request.session['session_task']
            # Перевод законченных задач из сессии в бд
            complete_session_task = get_complete_session_task(request)
            if complete_session_task:
                complete_session_task_transfer(user, complete_session_task)
                # Очищаем законченные задачи из сессии
                del request.session['complete_session_task']

            task = Task.objects.create(user=user,
                                       title=new_task,
                                       is_completed=False)

            task_html = render(request, 'notes/task/task.html', {'task': task}).content.decode('utf-8')

            return JsonResponse({'message': f'Задача c task-id: {task.id} и task-title: "{task.title}" успешно создана!',
                                 'task_html': task_html,
                                 'is_completed': task.is_completed,
                                 'created_at': task.created_at.isoformat()
                                 }, status=200)

        # Неавторизованный пользователь
        print('Пришел POST запрос в create_task_view для добавления новой задачи от неавторизованного пользователя')
        session_task = get_session_task(request)
        task_id = str(uuid.uuid4())
        task_data = {
            'title': new_task,
            'is_completed': False,
            'created_at': timezone.now().isoformat(),
        }
        session_task[task_id] = task_data
        request.session['session_task'] = session_task

        task_html = render(request, 'notes/task/task.html', {
            'task': {'id': task_id, **task_data},
        }).content.decode('utf-8')

        return JsonResponse({'message': f"Задача с task-id: {task_id} и task-title: {task_data['title']} успешно создана",
                             'task_html': task_html, 'is_completed': task_data["is_completed"]}, status=200)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def _get_task_or_complete_task(uuid_task_id: uuid.UUID) -> Union[Task, CompleteTask] | None:
    """
    Получить задачу по uuid_task_id
    """
    try:
        return Task.objects.get(id=uuid_task_id)
    except Task.DoesNotExist:
        try:
            return CompleteTask.objects.get(id=uuid_task_id)
        except CompleteTask.DoesNotExist:
            return None


def _update_db_task(task_obj: Task, task_value: str) -> Task:
    """
    Обновление задачи(DB)
    """
    task_obj.title = task_value
    task_obj.save()
    # Логгер для времени обновления
    return task_obj


def _update_session_task(session_dict: dict, str_uuid_task_id: str, task_value: str):
    """
    Обновление задачи(сессия)
    """
    task = session_dict.get(str_uuid_task_id)
    if task:
        task['title'] = task_value
        task['updated_at'] = timezone.now().isoformat()
        session_dict[str_uuid_task_id] = task
    return task


def update_task_view(request: HttpRequest, uuid_task_id) -> JsonResponse:
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            task_value = data.get('taskValue')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные'}, status=400)

        # Обноавление задачи для авторизованного пользователя
        if request.user.is_authenticated:
            print(f'Пришел PUT запрос в update_task_view на обновление задачи task-id: {uuid_task_id} от авторизованного пользователя: {request.user}')
            user = request.user
            task = _get_task_or_complete_task(uuid_task_id)

            if not task:
                return JsonResponse({'error': 'Ошибка при обновлении, задача не найдена в бд!'}, status=404)

            # Проверка прав на изменение задачи
            if not has_permissions(user, task.user):
                return JsonResponse({'error': 'Доступ заперещен!'}, status=403)

            task = _update_db_task(task, task_value)
            return JsonResponse({'message': 'Успешное обновление задачи',
                                 'task': {'task_id': task.id, 'task_title': task.title}
                                 }, status=200)

        # Обновление задачи для неавторизованного пользователя
        print(f'Пришел PUT запрос в update_task_view на обновление задачи task-id: {uuid_task_id} от неавторизованного пользователя')
        # Обновление для незавершенной задачи
        str_uuid_task_id = str(uuid_task_id)
        session_task = get_session_task(request)

        if str_uuid_task_id not in session_task:
            # Обновление для завершенной задачи
            complete_session_task = get_complete_session_task(request)
            if str_uuid_task_id not in complete_session_task:
                return JsonResponse({'error': 'Ошибка при обновлении, задача не найдена в сесии!'}, status=404)

            complete_task = _update_session_task(complete_session_task, str_uuid_task_id, task_value)
            # Сохраняем состояние сессии
            request.session['complete_session_task'] = complete_session_task
            return JsonResponse({'message': 'Успешное обновление задачи!',
                                 'task': {'task_id': str_uuid_task_id, 'task_title': complete_task['title']}
                                 }, status=200)

        task = _update_session_task(session_task, str_uuid_task_id, task_value)
        # Сохраняем состояние сессии
        request.session['session_task'] = session_task
        return JsonResponse({'message': 'Успешное обновление задачи!',
                             'task': {'task_id': str_uuid_task_id, 'task_title': task['title']}
                             }, status=200)

    return JsonResponse({'error': 'Только PUT запросы!'}, status=405)


def _delete_session_task(session_dict: dict, str_uuid_task_id: str) -> bool:
    """
    Удаление задачи(сессия)
    """
    if str_uuid_task_id in session_dict:
        task = session_dict.pop(str_uuid_task_id)
        if task:
            return True
        return False
    return False


def delete_task_view(request: HttpRequest, uuid_task_id: uuid.UUID) -> JsonResponse:
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            # Удаление задачи для авторизованного пользователя
            print(f'Пришел DELETE запрос в delete_task_view на удаление задачи task-id: {uuid_task_id} от авторизованного пользователя: {request.user}')
            user = request.user
            task = _get_task_or_complete_task(uuid_task_id)
            if not task:
                return JsonResponse({'error': 'Ошибка при удалении задачи, задача не найдена в бд!'}, status=404)

            # Проверка прав на удаление задачи
            if not has_permissions(user, task.user):
                return JsonResponse({'error': 'Доступ заблокирован'}, status=403)

            task.delete()
            return JsonResponse({'message': 'Задача успешно удалена'}, status=200)

        # Удаление задачи для неавторизованного пользователя
        print(f'Пришел DELETE запрос в delete_task_view на удаление задачи task-id: {uuid_task_id} от неавторизованного пользователя')
        str_uuid_task_id = str(uuid_task_id)
        # Удаление незавершенной задачи
        session_task = get_session_task(request)
        if str_uuid_task_id in session_task:
            is_deleted = _delete_session_task(session_task, str_uuid_task_id)
            request.session['session_task'] = session_task
            return JsonResponse({'message': 'Задача успешно удалена!'}, status=200)

        # Удаление завершенной задачи
        complete_session_task = get_complete_session_task(request)
        if str_uuid_task_id in complete_session_task:
            is_deleted = _delete_session_task(complete_session_task, str_uuid_task_id)
            request.session['complete_session_task'] = complete_session_task
            return JsonResponse({'message': 'Задача успешно удалена!'}, status=200)

        return JsonResponse({'error': 'Ошибка при удалении задачи, задача не найдена в сессии'}, status=404)
    return JsonResponse({'error': "Только DELETE запросы!"}, status=405)


def _complete_task_for_authenticated_user(user: str, uuid_task_id: uuid.UUID):
    # Декомпозиция complete_task_view для авторизованного пользователя
    ...


def _complete_task_for_guest(request: HttpRequest, uuid_task_id: uuid.UUID):
    # Декомпозиция complete_task_view для неавторизованного пользователя
    ...


def complete_task_view(request: HttpRequest, uuid_task_id: uuid.UUID) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST запросы!'}, status=405)

    # Завершение задачи для авторизованного пользователя
    if request.user.is_authenticated:
        print(f'Пришел запрос в {complete_task_view.__name__} для завершения задачи от авторизованного пользователя - {request.user}')
        user = request.user
        try:
            task = Task.objects.get(id=uuid_task_id)
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Задача не найдена!'}, status=404)

        # Проверка прав на завершение задачи
        if not has_permissions(user, task.user):
            return JsonResponse({'error': 'Доступ запрещен!'}, status=403)

        # Перенос задачи в заврешенные
        try:
            complete_task = CompleteTask.objects.create(id=task.id,
                                                        user=user,
                                                        title=task.title,
                                                        created_at=task.created_at,
                                                        updated_at=task.updated_at,
                                                        completed_at=timezone.now(),
                                                        is_completed=True)
        except IntegrityError:
            return JsonResponse({'error': 'Ошибка при завершении задачи!'}, status=404)

        task.delete()
        return JsonResponse({'message': 'Задача переведена в список завершенных!'}, status=200)

    # Завершение задачи для неавторизованного пользователя
    print(f'Пришел запрос в {complete_task_view.__name__} для завершения задачи от неавторизованного пользователя!')
    session_task = get_session_task(request)
    complete_session_task = get_complete_session_task(request)
    str_task_id = str(uuid_task_id)

    task = session_task.get(str_task_id)
    if not task:
        return JsonResponse({'error': f'Ошибка при завершении задачи!'}, status=404)

    # Перенос задачи
    task['is_completed'] = True
    task['completed_at'] = timezone.now().isoformat()
    complete_session_task[str_task_id] = task
    del session_task[str_task_id]

    # Сохранение состояния сессий
    request.session['session_task'] = session_task
    request.session['complete_session_task'] = complete_session_task

    return JsonResponse({'message': 'Задача переведена в список завершенных!', 'is_completed': task['is_completed']}, status=200)


def _incomplete_task_for_authenticated_user(user: str, task_id: uuid.UUID):
    # Декомпозиция incomplete_task_view для авторизованного пользователя
    ...


def _incomplete_task_for_guest(request: HttpRequest, task_id: uuid.UUID):
    # Декомпозиция incomplete_task_view для неавторизованного пользователя
    ...


def incomplete_task_view(request: HttpRequest, uuid_task_id: uuid.UUID) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST запросы!'}, status=405)
    # Возврат задачи в статус незавершенной для авторизованного пользователя
    if request.user.is_authenticated:
        print(f'Пришел запрос в {complete_task_view.__name__} от авторизованного пользователя для возврата задачи!')
        user = request.user
        try:
            complete_task = CompleteTask.objects.get(id=uuid_task_id)
        except CompleteTask.DoesNotExist:
            return JsonResponse({'error': 'Завершенная задача не найдена!'}, status=404)

        # Проверка прав на завершение задачи
        if not has_permissions(user, complete_task.user):
            return JsonResponse({'error': 'Доступ запрещен!'}, status=403)

        # Перенос задачи в незавершенные
        try:
            task = Task.objects.create(id=uuid_task_id,
                                       user=complete_task.user,
                                       title=complete_task.title,
                                       created_at=complete_task.created_at,
                                       updated_at=complete_task.updated_at,
                                       is_completed=False)
        except IntegrityError:
            return JsonResponse({'error': 'Ошибка при переводе задачи в незавершенные'}, status=404)

        complete_task.delete()
        return JsonResponse({'message': 'Задача переведена в список незавершенных!'}, status=200)

    # Возврат задачи в статус незавершенной для неавторизованного пользователя
    print(f'Пришел запрос в {complete_task_view.__name__} от неавторизованного пользователя для возврата задачи!')
    session_task = get_session_task(request)
    complete_session_task = get_complete_session_task(request)
    str_uuid_task_id = str(uuid_task_id)

    task = complete_session_task.get(str_uuid_task_id)
    if not task:
        return JsonResponse({'error': f'Задача не найдена в сесии!'}, status=404)

    # Перевод задачи в статус незавершенной
    task['is_completed'] = False
    task.pop('completed_at', None)
    session_task[str_uuid_task_id] = task
    del complete_session_task[str_uuid_task_id]

    # Сохраненение состояний сессий
    request.session['session_task'] = session_task
    request.session['complete_session_task'] = complete_session_task

    return JsonResponse({'message': 'Задача переведена в список незавершенных!', 'is_completed': task['is_completed']}, status=200)


def authorization_view(request: HttpRequest) -> HttpResponse | JsonResponse:
    if request.method == "GET":
        print('Пришел GET запрос в authorization_view')
        return render(request, 'notes/authorization.html')
    return JsonResponse({'error': 'Только GET запросы!'}, status=405)


def authorization_form_view(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        print('Пришел POST запрос в authorization_form_view')
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


def registration_view(request: HttpRequest) -> HttpResponse | JsonResponse:
    if request.method == 'GET':
        print('Пришел GET запрос в registration_view')
        return render(request, 'notes/registration.html')
    return JsonResponse({'error': 'Только GET запросы!'}, status=405)


def registration_form_view(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        print('Пришел POST запрос в registration_form_view')
        try:
            data = json.loads(request.body)
            user_login = data.get('login')
            user_email = data.get('email')
            user_password = data.get('password')

            if not user_login or not user_email or not user_password:
                return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

            is_create = create_new_user(user_login, user_email, user_password, request)

            if is_create is None:
                return JsonResponse({'error': 'Внутренняя ошибка при создании пользователя!'}, status=500)

            if not is_create:
                return JsonResponse({'error': 'Пользователь с таким Login или Email уже существует'}, status=400)

            return JsonResponse({
                'message': f'Успешная регистрация пользователя {user_login}',
                'username': user_login,
                'redirect_url': reverse('main')}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные!'}, status=400)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def logout_view(request: HttpRequest) -> HttpResponse:
    print('Пришел запрос в logout_view')
    logout(request)
    session_task = get_session_task(request)
    if session_task:
        session_task.clear()
    return redirect('main')


def password_reset_view(request: HttpRequest) -> HttpResponse | JsonResponse:
    if request.method == 'GET':
        print('Пришел GET запрос в password_reset_view')
        return render(request, 'notes/password-reset.html')
    return JsonResponse({'error': 'Только GET запросы!'}, status=405)


def password_reset_form_view(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        print('Пришел POST запрос в password_reset_form_view')
        try:
            data = json.loads(request.body)
            user_email = data.get('email')
            if not user_email:
                return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

            user = is_user_exist(user_email=user_email)
            if not user:
                return JsonResponse({'error': 'Пользователя с введенным email не существует'}, status=400)

            # Token Generation
            token = generate_reset_token()
            # Token Save in Data Base
            PasswordResetToken.objects.create(user=user, token=token)
            # Send email with token
            reset_url = request.build_absolute_uri(reverse('password_reset_confirm', args=[token]))
            subject, plain_message, html_message = generate_recovery_message(reset_url)

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


def password_reset_confirm_view(request: HttpRequest, token) -> HttpResponse | JsonResponse:
    if request.method == 'POST':
        print(f'Пришел POST запрос в password_reset_confirm_view c token: {token}')
        data = json.loads(request.body)
        new_password = data.get('new_password')
        password_confirm = data.get('password_confirm')

        if not new_password or not password_confirm:
            return JsonResponse({'error': 'Заполните все поля данными!'}, status=400)

        if new_password != password_confirm:
            return JsonResponse({'error': 'Пароли не совпадают'}, status=400)

        reset_token = PasswordResetToken.objects.filter(token=token).first()
        if not reset_token:
            return JsonResponse({'error': 'Недействительный токен'}, status=400)

        # Check token time
        if reset_token.created_at < timezone.now() - timedelta(hours=1):
            return JsonResponse({'error': 'Срок действия токена истек'}, status=400)

        # Update password
        user = reset_token.user  #
        user.password = make_password(new_password)
        user.save()

        reset_token.delete()

        return JsonResponse({
            'instruction_message': 'Пароль успешно изменен!',
            'redirect_url': reverse('main'),
        }, status=200)
    elif request.method == 'GET':
        print('Пришел GET запрос в password_reset_confirm_view')
        return render(request, 'notes/password-reset-confirm.html', {'token': token})
    else:
        return JsonResponse({'error': 'Только POST или GET запросы!'}, status=405)
