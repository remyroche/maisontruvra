// website/source/js/pages/register.js
import { fetchAPI } from '../api.js';
import { saveToken, isLoggedIn } from '../auth.js';
import { showToast } from '../ui.js';
import { attachPasswordValidator } from '../password-validator.js';
import { api } from '../api.js';
import { setSession } from '../session.js';

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        // Add this line to attach the validator
        attachPasswordValidator('register-form', 'password', 'password-requirements');

        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await api.auth.register(data.first_name, data.last_name, data.email, data.password);
                
                // Assuming the API returns a token and user details upon successful registration
                if (response && response.access_token) {
                    setSession(response.access_token, response.user);
                    // Redirect to the user's account page
                    window.location.href = '/compte.html';
                } else {
                    alert('Une erreur inattendue est survenue lors de la création de votre compte.');
                }
            } catch (error) {
                console.error('Registration failed:', error);
                alert(`L'inscription a échoué: ${error.message}`);
            }
        });
    }
});

async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  if (data.password !== data.confirm_password) {
    showToast("Passwords do not match.", 'error');
    return;
  }
  
  const submitButton = form.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = 'Registering...';

  try {
    // 1. Register the user
    await fetchAPI('/auth/register', {
      method: 'POST',
      body: {
        email: data.email,
        password: data.password
      },
    });

    // 2. Automatically log them in
    const loginData = await fetchAPI('/auth/login', {
        method: 'POST',
        body: {
            email: data.email,
            password: data.password
        }
    });

    // 3. Save the token and redirect
    saveToken(loginData.access_token);
    showToast('Registration successful! Redirecting...', 'success');
    
    setTimeout(() => {
        window.location.href = '/compte.html';
    }, 1500);

  } catch (error) {
    // Error toast is handled by fetchAPI
    submitButton.disabled = false;
    submitButton.textContent = 'Register';
  }
}
