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

export async function dataTransfer(form, formData, successCallback = null, errorCallback = null) {
    try {
        let response = await fetch(form.dataset.url, {
            method: 'POST',
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
                alert(result.error || 'Ошибка. Проверьте введенные данные');
                return null;
            }

            console.log(result.message);

            if (result.instruction_message) {
                alert(result.instruction_message);
            }
            if (result.redirect_url) {
                setTimeout(() => {
                    window.location.href = result.redirect_url;
                }, 500);
            }
            // if (result.new_task) {
            //     addTaskToDom(result.new_task);
            // }

            if (result.task_html) {
                let newTaskElement = addTaskToDom(result.task_html);
                attachDeleteHandler(newTaskElement)
            }

            return result;
        } else {
            console.error("Ошибка: Сервер вернул не JSON!");
            alert("Ошибка сервера. Попробуйте позже.");
            return null;
        }
    } catch (error) {
        console.error("Обнаружена ошибка попробуйте позже");
    }
}

function addTaskToDom(taskHTML) {
    let taskContainer = document.querySelector('#task-container');
    taskContainer.insertAdjacentHTML('beforeend', taskHTML);  //
    return taskContainer.lastElementChild; //
}

function attachDeleteHandler(taskElement) {
    let deleteButton = taskElement.querySelector('.delete-task');
    if (deleteButton) {
        deleteButton.addEventListener('click', async function(){
            let taskId = deleteButton.dataset.taskId;

            let response = await fetch(`/delete-task/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });

            if (response.ok) {
                taskElement.remove();
            } else {
                alert('Ошибка удаления!');
            }
        });
    }
}

// function addTaskToDom(newTask) {
//     let taskContainer = document.querySelector('#task-container');
//
//     let taskItem = document.createElement('div');
//     taskItem.className = 'task-item d-flex align-items-center justify-content-between p-3 mb-2 bg-white shadow-sm rounded';
//
//     let form = document.createElement('form');
//     form.className = 'task-form';
//     form.dataset.taskId = newTask.id;
//
//     form.innerHTML = `
//         <input type="text" class="task" name="task-title" id="task-${newTask.id}" value="${newTask.title}">
//         <label for="task-${newTask.id}" class="visually-hidden">Task</label>
//     `;
//
//     let deletionButton = document.createElement('button');
//     deletionButton.className = 'btn btn-link text-danger p-0 ms-2 delete-task';
//     deletionButton.dataset.taskId = newTask.id;
//     deletionButton.innerHTML = `<i class="bi bi-x-circle">`;
//
//
//     taskItem.appendChild(form);
//     taskItem.appendChild(deletionButton);
//     taskContainer.appendChild(taskItem);
// }

