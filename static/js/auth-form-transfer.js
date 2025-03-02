import { getCookie } from "./utilities";

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
            console.log(result.message);
            setTimeout(() => {
                window.location.href = result.redirect_url;
            }, 1000);
        } else {
            console.error('Ошибка', result.error);
            alert(result.error || 'Ошибка авторизации. Проверьте введенные данные.');
        }
    } catch (error) {
        console.error('Ошибка', error);
        alert('Ошибка соединения с сервером. Попробуйте позже!');
    }
};
