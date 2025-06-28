import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { defineRule, configure } from 'vee-validate';
import { required, email, min, confirmed, max } from '@vee-validate/rules';
import { localize } from '@vee-validate/i18n';
import fr from '@vee-validate/i18n/dist/locale/fr.json';

import App from './App.vue';
import router from './router';
import { useNotificationStore } from './stores/notification.js';
import './style.css';

// --- VeeValidate Global Configuration ---
defineRule('required', required);
defineRule('email', email);
defineRule('min', min);
defineRule('max', max);
defineRule('confirmed', confirmed);

configure({
  generateMessage: localize('fr', {
    messages: {
      ...fr.messages,
      required: 'Ce champ est requis',
      email: 'Veuillez saisir une adresse email valide',
      min: 'Ce champ doit contenir au moins 0:{length} caractères',
      max: 'Ce champ ne peut pas dépasser 0:{length} caractères',
      confirmed: 'Les mots de passe ne correspondent pas'
    }
  }),
  validateOnBlur: true,
  validateOnChange: true,
  validateOnInput: false,
});

// Create the Vue application instance
const app = createApp(App);

// Vue Global Error Handler
app.config.errorHandler = (err, instance, info) => {
  console.error("Unhandled Vue error:", err);
  console.error("Occurred in component:", instance ? instance.$.type.name : 'Unknown');
  console.error("Vue-specific info:", info);

  // Show user-friendly error notification
  try {
    const notificationStore = useNotificationStore();
    notificationStore.showNotification("Une erreur inattendue est survenue.", "error");
  } catch (e) {
    console.error("Failed to show error notification:", e);
  }
};

// Create the Pinia instance for state management
const pinia = createPinia();

// Use Pinia and the Router
app.use(pinia);
app.use(router);

// Mount the application to the DOM
app.mount('#app');