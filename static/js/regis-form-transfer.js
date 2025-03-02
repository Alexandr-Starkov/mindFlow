import { getCookie } from './utilities.js';


let form = document.querySelector('#regis-form'),
    // formInputs = document.querySelectorAll('.js-input'),
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

    try {
        let response = await fetch(form.dataset.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(formData)
        });

        let result = await response.json();
        if (response.ok) {
            console.log('Успех');
            setTimeout(() => {
                window.location.href = result.redirect_url;
            }, 1000);
        } else {
            console.error('Ошибка', result);
            alert(result.message || 'Ошибка регистрации. Проверьте введенные данные.');
        }
    } catch (error) {
        console.error('Ошибка', error);
        alert('Ошибка соединения с сервером. Попробуйте позже.');
    }
};
