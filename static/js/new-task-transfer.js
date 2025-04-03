import { dataTransfer } from "./utilities.js";


let form = document.querySelector('#new-task-form'),
    taskInput = form.querySelector('.new-task');

form.addEventListener('submit', async function(event) {
    event.preventDefault();

    let taskInputValue = taskInput.value.trim();

    if (taskInputValue) {
        let formData = {
            'newTask': taskInputValue,
        };
        await dataTransfer(form, formData);
    } else {
        return;
    }

    taskInput.value = '';
    taskInput.blur();
})
