// website/source/js/stores/auth.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '../api-client.js';
import { useNotificationStore } from './notification.js';

export const useAuthStore = defineStore('auth', () => {
    // STATE
    const user = ref(null);
    const isLoading = ref(false);
    const isAuthenticated = ref(false); // Sera déterminé par la présence d'un cookie HttpOnly

    // ACTIONS
    async function login(credentials) {
        const notificationStore = useNotificationStore();
        isLoading.value = true;
        try {
            await apiClient.post('/b2b/auth/login', credentials);
            // Le cookie HttpOnly est maintenant défini par le serveur.
            // La redirection est gérée par la page après un appel réussi.
            notificationStore.showNotification('Connexion réussie ! Redirection...', 'success');
            return true;
        } catch (error) {
            notificationStore.showNotification(error.message || 'Échec de la connexion', 'error');
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    async function register(prospect) {
        const notificationStore = useNotificationStore();
        isLoading.value = true;
        try {
            const payload = {
                company_name: prospect.companyName,
                siret: prospect.siret,
                contact_name: prospect.contactName,
                email: prospect.email,
                password: prospect.password,
            };
            const response = await apiClient.post('/b2b/auth/register', payload);
            notificationStore.showNotification(response.message, 'success');
            return true;
        } catch (error) {
            notificationStore.showNotification(error.message || "Erreur lors de l'inscription", 'error');
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    async function requestPasswordReset(email) {
        const notificationStore = useNotificationStore();
        isLoading.value = true;
        try {
            const response = await apiClient.post('/b2b/auth/request-password-reset', { email });
            notificationStore.showNotification(response.message, 'success');
            return true;
        } catch (error) {
            notificationStore.showNotification(error.message || "Erreur lors de la demande", 'error');
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    // On suppose que le backend gère la session.
    // Une fonction `checkAuthStatus` pourrait appeler un endpoint `/me` pour populer `user`.
    async function checkAuthStatus() {
        try {
            const data = await apiClient.get('/b2b/auth/me'); // Endpoint à créer
            user.value = data;
            isAuthenticated.value = true;
        } catch (error) {
            user.value = null;
            isAuthenticated.value = false;
        }
    }


    return { user, isLoading, isAuthenticated, login, register, requestPasswordReset, checkAuthStatus };
});
