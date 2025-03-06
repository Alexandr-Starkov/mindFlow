import { dataTransfer } from './utilities.js';


let form = document.querySelector('#reset-form'),
    inputEmail = document.querySelector('.js-input-email');

form.onsubmit = async function (event) {
    event.preventDefault();

    let emailVal = inputEmail.value.trim();
    let formData = {
        email: emailVal,
    };

    await dataTransfer(form, formData);
};
