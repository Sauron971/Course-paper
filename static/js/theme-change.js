let currentTheme = localStorage.getItem('theme') || 'light';

document.addEventListener('DOMContentLoaded', function() {
    // Применяем сохраненную тему при загрузке страницы
    applyTheme();

    document.getElementById('theme-change').addEventListener('click', function() {
        changeTheme();
        // Сохраняем новую тему в localStorage
        localStorage.setItem('theme', currentTheme);

        // Отправляем новую тему на сервер
        fetch('/change-theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ theme: currentTheme }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        })
        .catch(error => console.error('Ошибка:', error));
    });
});

function changeTheme() {
    currentTheme = (currentTheme === 'light') ? 'dark' : 'light';
    applyTheme();
}

function applyTheme() {
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('theme-change-lb').innerText = '🌙';
    } else {
        document.body.classList.remove('dark-mode');
        document.getElementById('theme-change-lb').innerText = '☀️';
    }
}
