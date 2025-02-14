document.addEventListener('DOMContentLoaded', function () {
    let form = document.querySelector('#form'),
        inputEmail = document.querySelector('.js-input-email'),
        inputPassword = document.querySelector('.js-input-password');

    function validateEmail(email) {
        let re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(String(email).toLowerCase());
    }

    function validatePassword(password) {
        let re = /^(?=.*[A-Z])[a-zA-Zа-яА-Я0-9]{3,15}$/;
        return re.test(password);
    }

    function resetCustomValidity(input) {
        input.setCustomValidity('');
    }

    [inputEmail, inputPassword].forEach(input => {
        input.addEventListener('input', function () {
            resetCustomValidity(this);
        });
    });

    // Обработчик события submit для валидации
    form.addEventListener('submit', function (event) {
        let isValid = true;

        // Валидация email
        if (inputEmail.value === '') {
            inputEmail.setCustomValidity('Email is empty!');
            isValid = false;
        } else if (!validateEmail(inputEmail.value)) {
            inputEmail.setCustomValidity('Enter a valid email address: example@mail.com');
            isValid = false;
        } else {
            inputEmail.setCustomValidity('');
        }

        // Валидация пароля
        if (inputPassword.value === '') {
            inputPassword.setCustomValidity('Password is empty!');
            isValid = false;
        } else if (!validatePassword(inputPassword.value)) {
            inputPassword.setCustomValidity('Password must contain an uppercase character and be between 3 and 15 characters long.');
            isValid = false;
        } else {
            inputPassword.setCustomValidity('');
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
})
