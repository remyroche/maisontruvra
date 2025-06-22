// website/source/js/register.js
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.id !== 'page-register') {
        return;
    }

    const registrationForm = document.getElementById('registration-form');
    const registrationMessageElement = document.getElementById('registration-message');

    if (registrationForm) {
        registrationForm.addEventListener('submit', handlePublicRegistration);
    }

    async function handlePublicRegistration(event) {
        event.preventDefault();
        clearFormErrors(registrationForm);
        if (registrationMessageElement) registrationMessageElement.textContent = '';

        const emailField = registrationForm.querySelector('#register-email');
        const passwordField = registrationForm.querySelector('#register-password');
        const confirmPasswordField = registrationForm.querySelector('#register-confirm-password');
        const nomField = registrationForm.querySelector('#register-nom');
        const prenomField = registrationForm.querySelector('#register-prenom');

        let isValid = true;

        if (!prenomField || !prenomField.value.trim()) {
            setFieldError(prenomField, t('public.js.firstname_required', 'Le prénom est requis.'));
            isValid = false;
        }
        if (!nomField || !nomField.value.trim()) {
            setFieldError(nomField, t('public.js.lastname_required', 'Le nom est requis.'));
            isValid = false;
        }
        if (!emailField || !emailField.value || (typeof validateEmail === 'function' && !validateEmail(emailField.value))) {
            setFieldError(emailField, t('public.js.newsletter_invalid_email', 'Adresse e-mail invalide.'));
            isValid = false;
        }

        if (passwordField && confirmPasswordField) {
            const passwordComplexityKey = typeof validatePasswordComplexity === 'function' ? validatePasswordComplexity(passwordField.value) : null;
            if (passwordComplexityKey) {
                setFieldError(passwordField, t(passwordComplexityKey, 'Le mot de passe ne respecte pas les critères de complexité.'));
                isValid = false;
            } else if (passwordField.value !== confirmPasswordField.value) {
                setFieldError(confirmPasswordField, t('public.js.passwords_do_not_match', 'Les mots de passe ne correspondent pas.'));
                isValid = false;
            }
        } else {
            isValid = false; // Should not happen if form is correct
        }

        if (!isValid) {
            const errorMessage = t('public.js.fix_form_errors', 'Veuillez corriger les erreurs dans le formulaire.');
            if (registrationMessageElement) registrationMessageElement.textContent = errorMessage;
            else if (typeof showGlobalMessage === 'function') showGlobalMessage(errorMessage, "error");
            return;
        }

        const registrationData = {
            email: emailField.value,
            password: passwordField.value,
            first_name: prenomField.value,
            last_name: nomField.value,
            role: 'b2c_customer' // Default role for public registration
        };

        if (typeof showGlobalMessage === 'function') showGlobalMessage(t('public.js.creating_account', 'Création du compte en cours...'), "info");

        try {
            const result = await makeApiRequest('/auth/register', 'POST', registrationData);

            if (result.success) {
                const successMessage = result.message || t('public.js.registration_success', 'Inscription réussie ! Vous pouvez maintenant vous connecter.');
                if (typeof showGlobalMessage === 'function') showGlobalMessage(successMessage, "success");
                registrationForm.reset();
                if (registrationMessageElement) registrationMessageElement.textContent = successMessage;
            } else {
                const errorMessage = result.message || t('global.error_generic', 'Une erreur est survenue.');
                if (registrationMessageElement) registrationMessageElement.textContent = errorMessage;
                else if (typeof showGlobalMessage === 'function') showGlobalMessage(errorMessage, "error");
            }
        } catch (error) {
            console.error("Public Registration error:", error);
            const errorMessage = error.data?.message || t('global.error_generic', 'Une erreur réseau est survenue.');
            if (registrationMessageElement) registrationMessageElement.textContent = errorMessage;
            else if (typeof showGlobalMessage === 'function') showGlobalMessage(errorMessage, "error");
        }
    }

    // Helper functions (can be moved to ui.js or utils.js if used more broadly)
    function setFieldError(field, message) {
        if (!field) return;
        field.classList.add('border-red-500'); // Example error class
        const errorElement = document.createElement('p');
        errorElement.className = 'text-xs text-red-600 mt-1 error-message-field';
        errorElement.textContent = message;
        field.parentNode.insertBefore(errorElement, field.nextSibling);
    }

    function clearFormErrors(form) {
        form.querySelectorAll('.error-message-field').forEach(el => el.remove());
        form.querySelectorAll('.border-red-500').forEach(el => el.classList.remove('border-red-500'));
    }
});