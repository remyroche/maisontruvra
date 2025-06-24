// website/source/admin/js/admin_login.js
import { apiClient } from './api-client.js';

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('admin-login-form');
    const forgotPasswordLink = document.getElementById('forgot-password-link');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
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
    forgotPasswordLink.addEventListener('click', async (e) => {
        e.preventDefault();
        const email = prompt("Veuillez entrer votre adresse e-mail d'administrateur pour recevoir un lien de réinitialisation :");
        if (!email) return;

        try {
            const response = await adminAPI.post('/auth/forgot-password', { email });
            alert(response.message);
        } catch (error) {
            // Even on error, show a generic message to prevent leaking information
            alert("Si un compte admin avec cet email existe, un lien a été envoyé.");
        }
    });
});
