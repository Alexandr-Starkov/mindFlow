
document.addEventListener('DOMContentLoaded', function () {
    setupTaskHandlers();
});

export function getCookie(name) {
    /*
        Поиск и возврат искомых куки
     */
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export async function dataTransfer(form, formData, successCallback = null, errorCallback = null, method = 'POST') {
    /*
        Отправляет данные на бэк и обрабатывает результат
    */
    try {
        let response = await fetch(form.dataset.url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            console.error('Ошибка при запросе:', response.status);
            alert('Ошибка. Проверьте введенные данные');
            return null;
        }

        let contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Ошибка: Сервер вернул не JSON!');
            alert('Ошибка сервера. Попробуйте позже!');
            return null;
        }

        let result = await response.json();

        if (result.instruction_message) {
            console.log(result.message);
            alert(result.instruction_message);
        }

        if (result.redirect_url) {
            console.log(result.message);
            setTimeout(() => {
                window.location.href = result.redirect_url;
            }, 500);
        }

        if (result.task_html) {
            console.log(result.message);
            addTaskToDom(result.task_html);
        }

        return result;
    } catch (error) {
        console.error("Обнаружена ошибка попробуйте позже");
        alert("Ошибка попробуйте позже!");
    }
}

function addTaskToDom(taskHTML) {
    /*
        Добавление блока разметки в DOM дерево
    */
    let taskContainer = document.querySelector('#task-container');
    taskContainer.insertAdjacentHTML('afterbegin', taskHTML);  //
}

function setupTaskHandlers() {
    /*
         Установка обработчиков для динамически добавленных заметок (делегирование событий)
    */
    const taskContainer = document.querySelector('#task-container');
    if (!taskContainer || taskContainer.dataset.setup) return;

    // Помечаем контейнер как обработанный
    taskContainer.dataset.setup = 'true';

    // Выделение текста при фокусе
    taskContainer.addEventListener('focus', function (event) {
        let taskInput = event.target.closest('.task')
        if (taskInput) {
            taskInput.select();
        }
    }, true);

    // Обновление задачи (делегирование событий)
    taskContainer.addEventListener('submit', async function(event) {
        let form = event.target.closest('.task-form');
        if (!form) return;

        event.preventDefault();
        let taskInput = form.querySelector('.task');

        let taskInputValue = taskInput.value.trim() || '-';
        let formData = { taskValue: taskInputValue };

        let result = await dataTransfer(form, formData, null, null, 'PUT');
        if (result && result.task) {
            console.log(`Значение заметки TaskId: ${result.task.task_id} обновлено на TaskValue: ${result.task.task_title}`);
            taskInput.value = result.task.task_title;
        } else {
            console.error(result.error);
            alert(result.error || 'Ошибка обновления!');
        }
        setTimeout(() => taskInput.blur(), 100);
    });

    // Удаление задачи (делегирование событий)
    taskContainer.addEventListener('click', async function (event) {
        let deleteButton = event.target.closest('.delete-task');
        if (deleteButton) {
            let taskElement = deleteButton.closest('.task-item');
            let taskId = deleteButton.dataset.taskId;

            try {
                let response = await fetch(`/delete-task/${taskId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    }
                });

                if (!response.ok) {
                    console.error(`Ошибка удаления:`, response.status);
                }

                let result = await response.json();
                console.log(result.message);
                taskElement.remove();
            } catch (error) {
                console.error(error);
                alert('Ошибка при удалении задачи!');
            }
        }
    });
}
