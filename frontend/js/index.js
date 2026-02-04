const API_BASE_URL = '/api';
let selectedRoles = [];
let jobId = null;
let statusInterval = null;

// Загрузка ролей при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/roles`);
        if (!response.ok) {
            throw new Error('Ошибка загрузки ролей');
        }
        const role_response = await response.json();
        selectedRoles = [...role_response.roles];
        renderRoles();
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('rolesContainer').innerHTML =
            '<div class="error">Не удалось загрузить роли</div>';
    }
});

// Рендеринг ролей
function renderRoles() {
    const container = document.getElementById('rolesContainer');
    container.innerHTML = '';

    if (selectedRoles.length === 0) {
        container.innerHTML = '<div class="status-text">Нет выбранных ролей</div>';
        return;
    }

    selectedRoles.forEach((role, index) => {
        const roleElement = document.createElement('div');
        roleElement.className = 'role-tag';
        roleElement.innerHTML = `
            ${role}
            <span class="remove" onclick="removeRole(${index})">×</span>
        `;
        container.appendChild(roleElement);
    });
}

// Удаление роли
window.removeRole = function(index) {
    selectedRoles.splice(index, 1);
    renderRoles();
};

// Добавление новой роли
document.getElementById('addRoleBtn').addEventListener('click', () => {
    const newRoleInput = document.getElementById('newRoleInput');
    const newRole = newRoleInput.value.trim();

    if (newRole && !selectedRoles.includes(newRole)) {
        selectedRoles.push(newRole);
        renderRoles();
        newRoleInput.value = '';
    }
});

// Валидация файла
document.getElementById('fileInput').addEventListener('change', (e) => {
    const file = e.target.files[0];
    const errorElement = document.getElementById('fileError');

    if (file) {
        const allowedExtensions = ['.txt', '.pdf', '.docx', '.md'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            errorElement.textContent = 'Неверный формат файла. Разрешены: txt, pdf, docx, md';
            errorElement.style.display = 'block';
            e.target.value = '';
        } else {
            errorElement.style.display = 'none';
        }
    }
});

// Отправка формы
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        document.getElementById('fileError').textContent = 'Выберите файл';
        document.getElementById('fileError').style.display = 'block';
        return;
    }

    if (selectedRoles.length === 0) {
        alert('Выберите хотя бы одну роль');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('settings', JSON.stringify({ roles: selectedRoles }));

    try {
        document.getElementById('submitBtn').disabled = true;
        document.getElementById('submitBtn').innerHTML = '<div class="spinner"></div> Оценка...';

        const response = await fetch(`${API_BASE_URL}/estimate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Ошибка отправки файла');
        }

        const data = await response.json();
        jobId = data.task_id || data.job_id;

        if (!jobId) {
            throw new Error('Не получен ID задания');
        }

        // Показать контейнер статуса
        document.getElementById('statusContainer').classList.add('show');
        document.getElementById('statusText').textContent = 'Оценка начата...';
        document.getElementById('progressBar').style.width = '10%';

        // Начать опрос статуса
        startStatusPolling();

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при отправке файла: ' + error.message);
        clearSubmitBtn();
    }
});

// Опрос статуса
function startStatusPolling() {
    statusInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/job/status/${jobId}`);

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Задание не найдено');
                }
                throw new Error('Ошибка получения статуса');
            }

            const status = await response.json();

            // Обновление прогресса
            const progress = status.progress || 0;
            document.getElementById('progressBar').style.width = `${Math.min(progress, 95)}%`;

            // Обновление текста статуса
            let statusText = 'Оценка...';
            if (status.estimation_stage === 'DONE') {
                statusText = 'Завершено!';
                document.getElementById('progressBar').style.width = '100%';
                clearInterval(statusInterval);
                clearSubmitBtn();
                fetchResult();
            } else if (status.estimation_stage === 'FAILED') {
                statusText = 'Ошибка';
                document.getElementById('progressBar').style.width = '0%';
                clearInterval(statusInterval);
                clearSubmitBtn();
            } else {
                statusText = `Прогресс: ${progress}%`;
            }

            document.getElementById('statusText').textContent = statusText;

        } catch (error) {
            console.error('Ошибка опроса статуса:', error);
            clearInterval(statusInterval);
            document.getElementById('statusText').textContent = 'Ошибка: ' + error.message;
        }
    }, 5000);
}

// Получение результата
async function fetchResult() {
    try {
        const response = await fetch(`${API_BASE_URL}/job/result/${jobId}`);

        if (!response.ok) {
            throw new Error('Результат не готов');
        }

        const result = await response.json();

        // Показать ссылку на скачивание
        if (result.is_success) {
            const downloadLink = document.createElement('a');
            downloadLink.href = `${API_BASE_URL}/job/download/${jobId}`;
            downloadLink.className = 'download-link';
            downloadLink.textContent = 'Сохранить файл';

            document.getElementById('resultContainer').innerHTML = '';
            document.getElementById('resultContainer').appendChild(downloadLink);
        }

    } catch (error) {
        console.error('Ошибка получения результата:', error);
        document.getElementById('statusText').textContent = 'Ошибка получения результата';
    }
}

function clearSubmitBtn() {
    document.getElementById('submitBtn').disabled = false;
    document.getElementById('submitBtn').innerHTML = "Отправить на оценку";
}