// website/source/pro/js/pro-register.js
import '../../js/i18n.js';
import { attachPasswordValidator } from '../../js/password-validator.js'; // Adjust path
import { proApi } from '../pro_api.js';

document.addEventListener('DOMContentLoaded', () => {
    const proRegisterForm = document.getElementById('pro-register-form');
    if (proRegisterForm) {
        // Add this line to attach the validator
        attachPasswordValidator('pro-register-form', 'password', 'password-requirements');
        
        proRegisterForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = new FormData(proRegisterForm);
            const data = Object.fromEntries(formData.entries());

            try {
                // Call the B2B registration API endpoint
                await proApi.auth.register({
                    company_name: data.company_name,
                    siret: data.siret,
                    first_name: data.first_name,
                    last_name: data.last_name,
                    email: data.email,
                    phone: data.phone,
                    password: data.password
                });

                alert('Votre compte professionnel a été créé avec succès. Vous allez être redirigé vers la page de connexion.');
                // Redirect to the professional login page
                window.location.href = '/pro/professionnels.html';
            } catch (error) {
                console.error('Professional registration failed:', error);
                alert(`La création du compte a échoué: ${error.message}`);
            }
        });
    }
});
