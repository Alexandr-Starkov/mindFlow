import { dataTransfer } from "./utilities.js";


document.addEventListener('DOMContentLoaded', function () {
    let taskForms = document.querySelectorAll('.task-form');

    taskForms.forEach(form => {
        let taskInput = form.querySelector('.task');

        taskInput.addEventListener('focus', function () {
            this.select();
        })

        form.addEventListener('submit', async function(event){
            event.preventDefault();

            let oldTaskInputValue = taskInput.value;
            let taskInputValue = taskInput.value.trim();
            if (!taskInputValue) {
                taskInputValue = '-';
            }


            let formData = {
                taskValue: taskInputValue,
            }

            const result = await dataTransfer(form, formData, null, null, 'PUT');

            if (result && result.task) {
                console.log(`TaskId: ${result.task.task_id}, TaskValue: ${oldTaskInputValue} обновлена на ${result.task.task_title}`);
                taskInput.value = result.task.task_title;
            }

            setTimeout(() => taskInput.blur(), 100);
        });
    });
});
