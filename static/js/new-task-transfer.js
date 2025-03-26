import { dataTransfer } from "./utilities.js";


let form = document.querySelector('#new-task-form'),
    newTaskInput = document.querySelector('#new-task');

form.onsubmit = async function(event) {
    event.preventDefault();

    let newTaskInputValue = newTaskInput.value.trim();

    if (newTaskInputValue) {
        let formData = {
            newTask: newTaskInputValue,
        };
        await dataTransfer(form, formData);
    } else {
        return;
    }
    newTaskInput.value = '';
    newTaskInput.blur();
}