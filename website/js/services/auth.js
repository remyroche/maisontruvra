
/**
 * @file /js/auth_service.js
 * @description Manages user authentication API calls and orchestrates state
 * updates via the Pinia store. It is now stateless and does not
 * store tokens directly.
 */
import { useAuthStore } from '../stores/auth.js';
import { apiClient } from './api.js';
import { useNotificationStore } from '../stores/notification.js';

export const authService = {
  /**
   * Validates user registration data
   */
  validateRegistration(data) {
    const errors = {};
    
    // Email validation
    if (!data.email) {
      errors.email = 'Email requis';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.email = 'Format email invalide';
    }
    
    // Password validation
    if (!data.password) {
      errors.password = 'Mot de passe requis';
    } else if (data.password.length < 8) {
      errors.password = 'Mot de passe doit contenir au moins 8 caractères';
    }
    
    // Name validation
    if (!data.first_name || data.first_name.length < 2) {
      errors.first_name = 'Prénom requis (min 2 caractères)';
    }
    
    if (!data.last_name || data.last_name.length < 2) {
      errors.last_name = 'Nom requis (min 2 caractères)';
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  },

  /**
   * Register a new user
   */
  async register(userData) {
    const validation = this.validateRegistration(userData);
    if (!validation.isValid) {
      throw new Error('Données invalides: ' + Object.values(validation.errors).join(', '));
    }

    try {
      const response = await apiClient.post('/auth/register', userData);
      return response;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.showNotification(error.message || 'Erreur lors de l\'inscription', 'error');
      throw error;
    }
  },

  /**
   * Login user
   */
  async login(email, password) {
    if (!email || !password) {
      throw new Error('Email et mot de passe requis');
    }

    try {
      const response = await apiClient.post('/auth/login', { email, password });
      
      if (response.requires_mfa) {
        return { requiresMfa: true, userId: response.user_id };
      }
      
      const authStore = useAuthStore();
      if (response.access_token) {
        authStore.setToken(response.access_token);
        await authStore.fetchProfile();
      }
      
      return response;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.showNotification(error.message || 'Erreur de connexion', 'error');
      throw error;
    }
  },

  /**
   * Verify MFA token
   */
  async verifyMfa(userId, mfaToken) {
    if (!userId || !mfaToken) {
      throw new Error('ID utilisateur et code MFA requis');
    }

    try {
      const response = await apiClient.post('/auth/login/verify-mfa', {
        user_id: userId,
        mfa_token: mfaToken
      });
      
      const authStore = useAuthStore();
      if (response.access_token) {
        authStore.setToken(response.access_token);
        await authStore.fetchProfile();
      }
      
      return response;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.showNotification(error.message || 'Code MFA invalide', 'error');
      throw error;
    }
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(email) {
    if (!email) {
      throw new Error('Email requis');
    }

    try {
      const response = await apiClient.post('/auth/password/request-reset', { email });
      const notificationStore = useNotificationStore();
      notificationStore.showNotification('Si un compte existe pour cet email, un lien de réinitialisation a été envoyé.', 'success');
      return response;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.showNotification('Erreur lors de la demande de réinitialisation', 'error');
      throw error;
    }
  },

  /**
   * Confirm password reset
   */
  async confirmPasswordReset(token, newPassword) {
    if (!token || !newPassword) {
      throw new Error('Token et nouveau mot de passe requis');
    }

    if (newPassword.length < 8) {
      throw new Error('Le mot de passe doit contenir au moins 8 caractères');
    }

    try {
      const response = await apiClient.post('/auth/password/confirm-reset', {
        token,
        new_password: newPassword
      });
      
      const notificationStore = useNotificationStore();
      notificationStore.showNotification('Mot de passe réinitialisé avec succès', 'success');
      return response;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.showNotification(error.message || 'Erreur lors de la réinitialisation', 'error');
      throw error;
    }
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      const authStore = useAuthStore();
      authStore.clearToken();
    }
  }
};
