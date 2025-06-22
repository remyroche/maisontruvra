/**
 * auth-portal-loader.js
 * Initialise et monte l'application Vue pour le portail d'authentification B2B.
 */
import AuthPortal from '../../js/vue/components/AuthPortal.vue';

document.addEventListener('DOMContentLoaded', () => {
  const mountEl = document.getElementById('auth-portal');
  if (mountEl) {
    const app = Vue.createApp(AuthPortal);
    // Vous pouvez fournir le client API ici si nécessaire
    // import apiClient from '../../js/api-client';
    // app.provide('apiClient', apiClient);
    app.mount(mountEl);
  }
});
