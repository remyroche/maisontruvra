// website/source/admin/js/admin_login.js
import { apiClient } from './api-client.js';

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('admin-login-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        apiClient.post('/admin/auth/login', { email, password })
            .then(data => {
                if (data && data.access_token) {
                    localStorage.setItem('admin_access_token', data.access_token);
                    window.location.href = '/admin/admin_dashboard.html';
                }
            })
            .catch(error => {
                // The apiClient already shows an error notification.
                // You could add specific logic here, like shaking the form.
                console.error('Admin login failed', error);
            });
    });
});
