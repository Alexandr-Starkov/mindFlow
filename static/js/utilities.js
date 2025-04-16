
document.addEventListener('DOMContentLoaded', function () {
    setupTaskTitleHandlers();
    setupTaskHandlers();
});

function checkTasks() {
    /*
        Добавляет d-none контейнеру отвечающему за вывод сообщения
     */
    const taskItems = document.querySelectorAll('.task-item');
    const message = document.getElementById('information-message-container');

    if (!message) return;

    if (taskItems.length === 0) {
        message.classList.remove('d-none');
        // showMessage();
    } else {
        // hideMessage();
        message.classList.add('d-none');
    }
}

// function showMessage() {
//     let message = document.getElementById('information-message-container');
//     message.classList.remove('hidden', 'fade-out');
//     message.classList.add('fade-in');
// }

// function hideMessage() {
//     let message = document.getElementById('information-message-container');
//     message.classList.remove('fade-in');
//     message.classList.add('fade-out');
//
//     message.addEventListener('transitionend', () => {
//         message.classList.add('hidden');
//     }, { once: true});
// }


export function getCookie(name) {
    /*
        Поиск и возврат искомых печенюх
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

        let contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Ошибка: Сервер вернул не JSON!');
            alert('Ошибка сервера. Попробуйте позже!');
            return null;
        }

        let result = await response.json();

        // Обработка ошибок
        if (result.error) {
            console.error('Ошибка:', result.error);
            if (typeof errorCallback === 'function') {
                errorCallback(result.error, result);
            } else {
                alert(result.error);
            }
        }

        // Обработка успешного сообщения
        if (result.message) {
            console.log('Сообщение:',result.message);
            if (typeof successCallback === 'function') {
                successCallback(result.message, result);
            }
        }

        // Перенаправление
        if (result.redirect_url) {
            setTimeout(() => {
                window.location.href = result.redirect_url;
            }, 500);
        }

        // Динамическое добавление HTML
        if (result.task_html) {
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
    taskContainer.insertAdjacentHTML("afterbegin", taskHTML);  //
    checkTasks();
}

function setupTaskTitleHandlers() {
    /*
        Установка обработчиков для динамически обновленного названия заметок (делегирование событий)
    */
    const headerNameContainer = document.querySelector('#header-name-container');
    if (!headerNameContainer || headerNameContainer.dataset.setup) return;
    headerNameContainer.dataset.setup = 'true';

    // Выделение текста при фокусе
    headerNameContainer.addEventListener('focus', function (event) {
        let headerNameInput = event.target.closest('.header-name-input');
        if (headerNameInput) {
            headerNameInput.select();
        }
    }, true);

    // Обновление header-name (делегирование событий)
    headerNameContainer.addEventListener('submit', async function(event) {
        let form = event.target.closest('.header-form');
        if (!form) return;

        event.preventDefault();
        let headerNameInput = form.querySelector('.header-name-input');
        let defaultValue = `My to-do list ${headerNameInput.dataset.defaultDate}`;
        let headerInputValue = headerNameInput.value.trim() || defaultValue;

        let formData = {
            newHeaderName: headerInputValue,
        };

        try {
            let result = await dataTransfer(form, formData);

            if (result && result.new_header_name) {
                headerNameInput.value = result.new_header_name;
                setTimeout(() => headerNameInput.blur(), 100);
            }
        } catch (error) {
            alert('Ошибка при обновлении Header-Title');
        }
    });
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
            // console.log(`Значение заметки TaskId: ${result.task.task_id} обновлено на TaskValue: ${result.task.task_title}`);
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

                let result = await response.json();

                if (!response.ok) {
                    console.error(`Ошибка удаления:`, response.status);
                    if (result.error) {
                        console.error(result.error);
                    }
                }
                console.log(result.message);
                taskElement.remove();
                checkTasks();
            } catch (error) {
                console.error(error);
                alert('Ошибка при удалении задачи!');
            }
        }
    });
}
