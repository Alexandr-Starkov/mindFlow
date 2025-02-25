
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
            alert('Вы успешно зарегистрированы!');
            window.location.href = result.redirect_url;
        } else {
            console.error('Ошибка', result);
            alert('Ошибка регистрации. Проверьте введенные данные.');
        }
    } catch (error) {
        console.error('Ошибка', error);
        alert('Ошибка соединения с сервером. Попробуйте позже.');
    }
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
