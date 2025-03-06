import {dataTransfer} from "./utilities.js";


let form = document.querySelector('#reset-confirm-form'),
    inputNewPassword = document.querySelector('.js-input-password'),
    inputPasswordConfirm = document.querySelector('.js-input-password-confirm');

form.onsubmit = async function (event) {
    event.preventDefault();

    let newPasswordVal = inputNewPassword.value.trim(),
        passwordConfirmVal = inputPasswordConfirm.value.trim();

    let formData = {
        'new_password': newPasswordVal,
        'password_confirm': passwordConfirmVal,
    };

    await dataTransfer(form, formData);
}