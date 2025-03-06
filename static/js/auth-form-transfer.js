import { dataTransfer } from "./utilities.js";


let form = document.querySelector('#auth-form'),
    inputLogin = document.querySelector('.js-input-login'),
    inputPassword = document.querySelector('.js-input-password');

form.onsubmit = async function (event) {
    event.preventDefault();

    let loginVal = inputLogin.value.trim(),
        passwordVal = inputPassword.value.trim();

    let formData = {
        login: loginVal,
        password: passwordVal,
    };

    await dataTransfer(form, formData);
};
