// Filename: website/source/js/password-validator.js
// This utility provides functions to validate a password against a strong policy.

/**
 * Validates a password against a defined policy.
 * @param {string} password - The password to validate.
 * @returns {object} An object with boolean flags for each requirement.
 */
function validatePassword(password) {
    const requirements = {
        length: password.length >= 12,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[!@#$%^&*]/.test(password),
    };
    return requirements;
}

/**
 * Updates the UI to show which password requirements are met.
 * @param {object} requirements - The object from validatePassword.
 * @param {HTMLElement} requirementsContainer - The DOM element containing the list of requirements.
 */
function updateRequirementsUI(requirements, requirementsContainer) {
    for (const key in requirements) {
        const el = requirementsContainer.querySelector(`#${key}-req`);
        if (el) {
            if (requirements[key]) {
                el.classList.add('valid');
                el.classList.remove('invalid');
            } else {
                el.classList.add('invalid');
                el.classList.remove('valid');
            }
        }
    }
}

/**
 * Attaches the password validator to a form.
 * @param {string} formId - The ID of the registration form.
 * @param {string} passwordFieldId - The ID of the password input field.
 * @param {string} requirementsContainerId - The ID of the element that displays the requirements.
 */
export function attachPasswordValidator(formId, passwordFieldId, requirementsContainerId) {
    const form = document.getElementById(formId);
    const passwordInput = document.getElementById(passwordFieldId);
    const requirementsContainer = document.getElementById(requirementsContainerId);
    const confirmPasswordInput = document.getElementById('confirm_password'); // Assuming this ID for confirm password

    if (!form || !passwordInput || !requirementsContainer) {
        console.error('Password validator could not find required elements.');
        return;
    }

    // Show requirements when the user starts typing
    passwordInput.addEventListener('focus', () => {
        requirementsContainer.style.display = 'block';
    });

    // Validate on every keystroke
    passwordInput.addEventListener('input', () => {
        const requirements = validatePassword(passwordInput.value);
        updateRequirementsUI(requirements, requirementsContainer);
    });

    // Prevent form submission if the password is not valid
    form.addEventListener('submit', (event) => {
        const requirements = validatePassword(passwordInput.value);
        const allValid = Object.values(requirements).every(val => val === true);
        const passwordsMatch = passwordInput.value === confirmPasswordInput.value;

        if (!allValid) {
            event.preventDefault();
            alert('Votre mot de passe ne respecte pas tous les critères de sécurité.');
            return;
        }

        if (confirmPasswordInput && !passwordsMatch) {
            event.preventDefault();
            alert('Les mots de passe ne correspondent pas.');
            return;
        }
    });
}
