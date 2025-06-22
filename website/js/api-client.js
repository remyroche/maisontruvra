// website/source/js/api-client.js
import { useNotificationStore } from './stores/notification.js';

/**
 * A centralized client for making API requests.
 * It automatically handles the CSRF token and provides consistent error handling
 * by using the notification store. It assumes the browser is handling session
 * management via HttpOnly cookies.
 */
class ApiClient {
    constructor() {
        this.baseUrl = '/api'; // Assumes API is on the same origin
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const notificationStore = useNotificationStore();

        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...options.headers,
        };

        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (csrfToken) {
            headers['X-CSRF-Token'] = csrfToken;
        }

        try {
            const response = await fetch(url, { ...options, headers });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: 'Une erreur de réseau est survenue.' }));
                // L'erreur est maintenant affichée via le store de notifications
                notificationStore.showNotification(errorData.message || `Erreur: ${response.statusText}`, 'error');
                throw new Error(errorData.message);
            }

            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            // L'erreur est déjà notifiée, on la propage pour que le code appelant puisse arrêter son exécution
            throw error;
        }
    }

    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    post(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) });
    }

    put(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) });
    }

    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
}

export const apiClient = new ApiClient();

