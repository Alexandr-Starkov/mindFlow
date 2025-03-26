import { dataTransfer } from "./utilities.js";


let form = document.querySelector('#header-form'),
    headerInput = document.querySelector('#default-text'),
    defaultDate = headerInput.dataset.defaultDate;

headerInput.addEventListener("focus", function () {
    this.select(); // Полное выделение при фокусе
});

form.onsubmit = async function(event) {
    event.preventDefault();

    let headerInputVal = headerInput.value.trim();

    if (!headerInputVal) {
        headerInput.value = `My to-do list ${defaultDate}`;
    } else {
        let formData = {
            headerName: headerInput.value,
        };

        let result = await dataTransfer(form, formData);

        if (result) {
            headerInput.value = result.new_title;
        }
    }
    headerInput.blur(); // Убрать фокус после отправки
};

