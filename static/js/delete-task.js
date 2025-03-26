import { getCookie } from "./utilities.js";


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-task").forEach(button => {
        button.addEventListener("click", function () {

            const taskId = this.getAttribute('data-task-id');

            fetch(`/delete-task/${taskId}`, {
                method: 'DELETE',
                headers: {
                    "X-CSRFToken": getCookie('csrftoken'),
                }
            })
            .then(response => {
                if (response.ok) {
                    document.getElementById(`task-${taskId}`).closest(".task-item").remove()
                } else {
                    console.error("error");
                }
            })
            .catch(error => console.error("Ошибка:", error));
        });
    });
});