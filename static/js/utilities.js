export function getCookie(name) {
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
        if (contentType && contentType.includes('application/json')) {
            let result = await response.json();

            if (!response.ok) {
                console.error('Ошибка', result.error);
                alert(result.error | 'Ошибка. Проверьте введенные данные');
                return null;
            }

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
        } else {
            console.error("Ошибка: Сервер вернул не JSON!");
            alert("Ошибка сервера. Попробуйте позже.");
            return null;
        }
    } catch (error) {
        console.error("Обнаружена ошибка попробуйте позже");
        alert("Ошибка попробуйте позже!");
    }
}

function addTaskToDom(taskHTML) {
    let taskContainer = document.querySelector('#task-container');
    taskContainer.insertAdjacentHTML('beforeend', taskHTML);  //
    setupTaskHandlers();
}

function setupTaskHandlers() {
    let taskContainer = document.querySelector('#task-container');

    if (!taskContainer) return;

    // Удаление задачи
    taskContainer.addEventListener('click', async function (event) {
        let deleteButton = event.target.closest('.delete-task');
        if (deleteButton) {
            let taskElement = deleteButton.closest('.task-item');
            let taskId = deleteButton.dataset.taskId;

            let response = await fetch(`/delete-task/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });

            let result = await response.json();

            if (response.ok) {
                console.log(result.message);
                taskElement.remove();
            } else {
                console.error(result.error);
                alert(result.error || 'Ошибка удаления');
            }
        }
    });

    // Обновление задачи
    taskContainer.querySelectorAll('.task-form').forEach((form) => {
        if (!form.dataset.setup) {
            form.dataset.setup = 'true';

            form.addEventListener('submit', async function(event) {
                event.preventDefault();

                let taskInput = form.querySelector('.task');
                let taskInputValue = taskInput.value.trim() || '-';

                let formData = { taskValue: taskInputValue };

                let result = await dataTransfer(form, formData, null, null, 'PUT');

                if (result && result.task) {
                    console.log(`TaskId: ${result.task.task_id}, TaskValue: ${taskInputValue} обновлена на ${result.task.task_title}`);
                    taskInput.value = result.task.task_title;
                } else {
                    console.error(result.error);
                    alert(result.error || 'Ошибка обновления!');
                }

                setTimeout(() => taskInput.blur(), 100);
            });
        }
    });

    // Выделение текста при фокусе
    taskContainer.addEventListener('focus', function (event) {
        let taskInput = event.target.closest('.task')

        if (taskInput) {
            taskInput.select();
        }

    }, true);
}
