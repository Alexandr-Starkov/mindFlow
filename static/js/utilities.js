
document.addEventListener('DOMContentLoaded', function () {
    setupTaskTitleHandlers();
    setupTaskHandlers('#task-container');
    setupTaskHandlers('#completed-task-container');
});

export function getCookie(name) {
    /*
        Поиск и возврат искомых cookies
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
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
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
                return;
            }
        }

        // Обработка успешного сообщения
        if (result.message) {
            console.log(result.message);
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
        alert("Обнаружена ошибка попробуйте позже!");
    }
}

function addTaskToDom(taskHTML) {
    /*
        Добавление блока разметки в DOM дерево
    */
    let taskContainer = document.querySelector('#task-container');
    taskContainer.insertAdjacentHTML("afterbegin", taskHTML);  //
    updateContainerVisibility();
}

function setupTaskTitleHandlers() {
    /*
        Установка обработчиков для заголовка (делегирование событий)
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

    // Обновление header-name
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

function setupTaskHandlers(containerSelector) {
    /*
        Установка обработчиков для контейнеров незавершенных/завершенных задач (делегирование событий)
    */
    let container = document.querySelector(containerSelector);
    if (!container || container.dataset.setup) return;

    // Помечаем контейнер как обработанный
    container.dataset.setup = 'true';

    // Выделение текста при фокусе
    container.addEventListener('focus', function (event) {
        let taskInput = event.target.closest('.task')
        if (taskInput) {
            taskInput.select();
        }
    }, true);

    // Обновление задачи
    container.addEventListener('submit', async function(event) {
        let form = event.target.closest('.task-form');
        if (!form) return;

        event.preventDefault();
        let taskInput = form.querySelector('.task');

        let taskInputValue = taskInput.value.trim() || '-';
        let formData = { taskValue: taskInputValue };

        let result = await dataTransfer(form, formData, null, null, 'PUT');

        if (result && result.task) {
            taskInput.value = result.task.task_title;
            setTimeout(() => taskInput.blur(), 100);
        }
    });

    // Обработчик для checkbox
    container.addEventListener('change', async function(event) {
        const checkBox = event.target.closest('.task-checkbox');
        if (!checkBox) return;

        const taskItem = checkBox.closest('.task-item');
        const isCompleted = checkBox.classList.contains('completed');
        const url = isCompleted ? checkBox.dataset.incompleteUrl : checkBox.dataset.completeUrl;

        if (checkBox) {
            try {
                let response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });

                let result = await response.json();
                if (result && result.message) {
                    const targetContainer = isCompleted
                        ? document.getElementById('task-container')
                        : document.getElementById('completed-task-container');

                    // Обновление классов
                    taskItem.classList.toggle('completed');
                    checkBox.classList.toggle('completed');
                    taskItem.querySelector('.task').classList.toggle('completed');

                    // Перемещение элемента
                    if (targetContainer.id === 'task-container') {
                        const inputTask = taskItem.querySelector('.task');
                        const returnedTaskCreatedAt = new Date(inputTask.dataset.createdAt);
                        const taskItems = Array.from(targetContainer.querySelectorAll('.task-item'))
                            .filter(item => item !== taskItem)
                            .sort((a, b) => {
                                const dateA = new Date(a.querySelector('.task').dataset.createdAt);
                                const dateB = new Date(b.querySelector('.task').dataset.createdAt);
                                return dateB - dateA;
                            })

                        let insertIndex = taskItems.findIndex(item => {
                            const itemDate = new Date(item.querySelector('.task').dataset.createdAt);
                            return returnedTaskCreatedAt > itemDate;
                        })

                        if (insertIndex === -1) {
                            insertIndex = taskItems.length;
                        }

                        if (insertIndex < taskItems.length) {
                            targetContainer.insertBefore(taskItem, taskItems[insertIndex]);
                        } else {
                            targetContainer.appendChild(taskItem);
                        }

                    } else if (targetContainer.id === 'completed-task-container') {
                        targetContainer.prepend(taskItem);
                    }
                    // Обновление видимости контейнера
                    updateContainerVisibility();
                } else {
                    console.error(result.error);
                    alert(result.error);
                }
            } catch (error) {
                console.error('Ошибка при завершении задачи!');
                alert('Ошибка при завершении задачи, попробуйте позже!');
            }
        }
    });

    // Удаление задачи
    container.addEventListener('click', async function (event) {
        let deleteButton = event.target.closest('.delete-task');
        if (deleteButton) {
            let taskElement = deleteButton.closest('.task-item');
            let taskId = deleteButton.dataset.taskId;

            try {
                let response = await fetch(`/delete-task/${taskId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });

                let result = await response.json();
                if (!response.ok) {
                    console.error(result.error);
                    alert(result.error);
                    return;
                }

                console.log(result.message);
                taskElement.remove();
                updateContainerVisibility();
            } catch (error) {
                console.error(error);
                alert('Ошибка при удалении задачи!');
            }
        }
    });
}

function updateContainerVisibility() {
    const completedContainerWrapper = document.querySelector('.completed-task-container');
    const messageContainer = document.getElementById('information-message-container');

    // Вывод сообщения о пустых задачах
    if (document.getElementById('task-container').children.length === 0) {
        messageContainer.classList.remove('d-none');
    } else {
        messageContainer.classList.add('d-none');
    }

    // Видимость контейнера для завершенных задач
    if (document.getElementById('completed-task-container').children.length === 0) {
        completedContainerWrapper.classList.add('d-none');
    } else {
        completedContainerWrapper.classList.remove('d-none');
    }
}


// function moveToCompleted(taskElement) {
//     /*
//         Перевод задач в список завершенных
//     */
//     taskElement.classList.add('completed');
//
//     const checkBox = taskElement.querySelector('.task-checkbox');
//     const inputTask = taskElement.querySelector('.task');
//     checkBox.classList.add('completed');
//     inputTask.classList.add('completed');
//
//     const completedTaskWrapper = document.querySelector('.completed-task-container');
//     const completedTaskContainer = document.querySelector('#completed-task-container');
//
//     if (completedTaskWrapper.classList.contains('d-none')) {
//         completedTaskWrapper.classList.remove('d-none');
//     }
//
//     completedTaskContainer.prepend(taskElement);
//     checkTasks();
// }
//
// function moveToIncompleted(taskElement) {
//     /*
//         Перевод задач в список незавершенных
//     */
//     taskElement.classList.remove('completed');
//
//     const checkBox = taskElement.querySelector('.task-checkbox');
//     const inputTask = taskElement.querySelector('.task');
//     checkBox.classList.remove('completed');
//     inputTask.classList.remove('completed');
//
//     const returnedTaskCreatedAt = inputTask.dataset.createdAt;
//     const taskContainer = document.querySelector('#task-container');
//     const taskInputs = taskContainer.querySelectorAll('.task')
//
//     for (let i = 0; i < taskInputs.length; i++) {
//         const taskInputCreatedAt = taskInputs[i].dataset.createdAt;
//         if (taskInputCreatedAt > returnedTaskCreatedAt) {
//             taskContainer.insertBefore(taskElement, taskInputs[i].closest('.task-item'));
//             hideCompletedWrapperIfEmpty();
//             return;
//         }
//     }
//     taskContainer.appendChild(taskElement);
//     hideCompletedWrapperIfEmpty();
// }
//
// function hideCompletedWrapperIfEmpty() {
//     /*
//         Скрывает блок законченных задач при пустом контейнере
//     */
//     const completedTaskWrapper = document.querySelector('.completed-task-container');
//     const remainingCompletedTasks = completedTaskWrapper.querySelectorAll('.task-item');
//
//     if (remainingCompletedTasks.length === 0) {
//         completedTaskWrapper.classList.add('d-none');
//     }
// }