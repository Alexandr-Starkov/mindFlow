export function getCookie(name) {
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

export async function dataTransfer(form, formData, successCallback = null, errorCallback = null) {
    try {
        let response = await fetch(form.dataset.url, {
            method: 'POST', headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            }, body: JSON.stringify(formData)
        });

        let result = await response.json();
        if (response.ok) {
            console.log(result.message);
            if (successCallback) {
                successCallback(result);
            } else {
                if (result.instruction_message) {
                    alert(result.instruction_message);
                }
                setTimeout(() => {
                window.location.href = result.redirect_url;
               }, 500);
            }
        } else {
            console.error('Ошибка', result.error);
            if (errorCallback) {
                errorCallback(result.error);
            } else {
                alert(result.error || 'Ошибка авторизации. Проверьте введенные данные.');
            }
        }
    } catch (error) {
        console.error('Ошибка', error);
        if (errorCallback) {
            errorCallback('Ошибка соединения с сервером. Попробуйте позже');
        } else {
            alert('Ошибка соединения с сервером. Попробуйте позже!');
        }
    }
}
