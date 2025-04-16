import json
import uuid
import datetime
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta, date

from .models import Task, PasswordResetToken, HeaderTitle
from tools.tools import (get_session_task, session_task_transfer, generate_reset_token,
                         generate_recovery_message, create_new_user, is_user_exist)


def main_view(request: HttpRequest) -> HttpResponse | JsonResponse:
    if request.method == 'GET':
        print('Пришел GET запрос в main_view')
        user_header_title = None
        session_task = get_session_task(request)
        if request.user.is_authenticated:
            print(f'Пришел запрос от авторизованного пользователя - {request.user}')
            user = request.user

            # Перенос сессионных задач, при наличии
            if session_task:
                session_task_transfer(user, session_task)
                del request.session['session_task']

            tasks = Task.objects.filter(user=user).order_by('-created_at')

            # Подтягиваем заголовок пользователя
            header_obj = HeaderTitle.objects.filter(user=user).first()
            if header_obj:
                user_header_title = header_obj.header_title
        else:
            # Подготовка и сортировка сессионных задач
            session_task_sorted = sorted(
                session_task.items(),
                key=lambda item: item[1]['created_at'],
                reverse=True
            )
            tasks = [{'id': key, **value} for key, value in session_task_sorted]

        context = {
            'date': date.today().strftime('%d/%m/%Y'),
            'tasks': tasks,
            'user_header_title': user_header_title,
        }
        return render(request, 'notes/index.html', context=context)
    return JsonResponse({'error': 'Только GET запросы!'}, status=405)


def create_task_view(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_task = data.get('newTask')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные!'}, status=400)

        if not new_task:
            return JsonResponse({'error': 'Заполните значение для заметки, название не должно быть пустым!'},
                                status=400)

        # Авторизованные пользователь
        if request.user.is_authenticated:
            print(f'Пришел POST запрос в create_task_view на добавление новой заметки от авторизованного пользователя {request.user}')
            user = request.user

            # Перевод заметок из сесии в бд
            session_task = get_session_task(request)
            if session_task:
                session_task_transfer(user, session_task)
                # Очищаем заметки из сессии
                del request.session['session_task']

            task = Task.objects.create(user=user, title=new_task)
            task_html = render(request, 'notes/task/task.html', {'task': task}).content.decode('utf-8')

            return JsonResponse({'message': f'Заметка c task-id: {task.id} и task-title: "{task.title}" успешно создана!',
                                 'task_html': task_html, 'is_completed': task.is_completed}, status=200)

        # Неавторизованный пользователь
        print('Пришел POST запрос в create_task_view для добавления новой заметки от неавторизованного пользователя')
        session_task = get_session_task(request)
        task_id = str(uuid.uuid4())
        task_data = {
            'title': new_task,
            'is_completed': False,
            'created_at': datetime.now().isoformat(),
        }
        session_task[task_id] = task_data
        request.session['session_task'] = session_task

        task_html = render(request, 'notes/task/task.html', {
            'task': {'id': task_id, **task_data},
        }).content.decode('utf-8')

        return JsonResponse({'message': f"Заметка с task-id: {task_id} и task-title: {task_data['title']} успешно создана",
                             'task_html': task_html, 'is_completed': task_data["is_completed"]}, status=200)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


def update_task_view(request, task_id) -> JsonResponse:
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            task_value = data.get('taskValue')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Проверьте введенные данные'}, status=400)

        # Обновление заметок для авторизованного пользователя
        if request.user.is_authenticated:
            print(f'Пришел PUT запрос в update_task_view на обновление заметки task-id: {task_id} от авторизованного пользователя')
            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                return JsonResponse({'error': f'task-id: {task_id} не найден в бд!'}, status=400)

            task.title = task_value
            task.save()
            return JsonResponse({'message': f'Успешное обновление заметки c task-id: {task_id}',
                                 'task': {'task_id': task.id, 'task_title': task.title}
                                 }, status=200)

        # Обновление заметок для неавторизованного пользователя
        print(f'Пришел PUT запрос в update_task_view на обновление заметки task-id: {task_id} от неавторизованного пользователя')
        task_id_str = str(task_id)
        session_task = get_session_task(request)
        task = session_task.get(task_id_str)
        if not task:
            return JsonResponse({'error': f'task_id: "{task_id}" не найден в session-task!'}, status=400)

        task['title'] = task_value
        session_task[task_id_str] = task
        request.session['session_task'] = session_task

        return JsonResponse({'message': f'Успешное обновление заметки с session-task-id "{task_id}"',
                             'task': {'task_id': task_id, 'task_title': task['title']}
                             }, status=200)

    return JsonResponse({'error': 'Только PUT запросы!'}, status=405)


def delete_task_view(request, task_id) -> JsonResponse:
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            print(f'Пришел DELETE запрос в delete_task_view на удаление заметки task-id: {task_id} от авторизованного пользователя')
            # Удаление заметок для авторизованного пользователя
            try:
                task: Task = Task.objects.get(id=task_id)
                task.delete()
                return JsonResponse({'message': f'Заметка task-id: "{task_id}" успешно удалена!'}, status=200)
            except Task.DoesNotExist:
                return JsonResponse({'error': f'task-id: "{task_id}" не найден в бд!'}, status=400)
        # Удаление заметок для неавторизованного пользователя
        print(f'Пришел DELETE запрос в delete_task_view на удаление заметки task-id: {task_id} от неавторизованного пользователя')
        task_id_str = str(task_id)
        session_task = get_session_task(request)
        task = session_task.get(task_id_str)
        if not task:
            return JsonResponse({'error': f'Заметка task-id: "{task_id}" не найдена в session-task!'}, status=400)

        del session_task[task_id_str]
        request.session['session_task'] = session_task
        return JsonResponse({'message': f'Заметка task-id: "{task_id}" успешно удалена из session-task'}, status=200)

    return JsonResponse({'error': "Только DELETE запросы!"}, status=405)


def update_header_name_view(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        print('Пришел POST запрос в update_header_name_view на обновление Header-Title')
        try:
            data = json.loads(request.body)
            new_header_name = data.get('newHeaderName')
            if not new_header_name:
                raise ValueError('Новое имя заголовка не может быть пустым!')
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
        header_obj.header_title = new_header_name
        header_obj.save()

        return JsonResponse({
            'message': f"Header-Title успешно {'создан' if created else 'обновлен'} на {new_header_name}",
            'new_header_name': header_obj.header_title,
        }, status=200)
    return JsonResponse({'error': 'Только POST запросы!'}, status=405)


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
