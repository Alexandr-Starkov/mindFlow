import { dataTransfer } from './utilities.js';


let form = document.querySelector('#regis-form'),
    inputLogin = document.querySelector('.js-input-login'),
    inputEmail = document.querySelector('.js-input-email'),
    inputPassword = document.querySelector('.js-input-password');

form.onsubmit = async function (event) {
    event.preventDefault();

    let loginVal = inputLogin.value.trim(),
        emailVal = inputEmail.value.trim(),
        passwordVal = inputPassword.value.trim();

    let formData = {
        login: loginVal,
        email: emailVal,
        password: passwordVal,
    };

    await dataTransfer(form, formData);
};
