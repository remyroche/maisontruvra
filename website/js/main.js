import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { defineRule, configure } from 'vee-validate';
import { required, email, min, confirmed, max } from '@vee-validate/rules';
import { localize } from '@vee-validate/i18n';
import fr from '@vee-validate/i18n/dist/locale/fr.json';
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import App from '../vue/App.vue';
import router from './router';
// Note: Assuming main.css is the entry point for styles
import '../css/main.css';

// --- VeeValidate Global Configuration ---
// Define validation rules globally for use in forms.
defineRule('required', required);
defineRule('email', email);
defineRule('min', min);
defineRule('max', max);
defineRule('confirmed', confirmed);

// Configure default error messages and validation behavior.
configure({
  generateMessage: localize('fr', {
    messages: {
      ...fr.messages, // Import default French messages
      required: 'Ce champ est requis',
      email: 'Veuillez saisir une adresse email valide',
      min: 'Ce champ doit contenir au moins 0:{length} caractères',
      max: 'Ce champ ne peut pas dépasser 0:{length} caractères',
      confirmed: 'Les mots de passe ne correspondent pas'
    }
  }),
  validateOnBlur: true,      // Validate when a user leaves a field
  validateOnChange: true,    // Validate when the value changes
  validateOnInput: false,      // Avoid validating on every keystroke for better performance
});
// --- End VeeValidate Configuration ---



// 1. Create the Vue application instance
const app = createApp(App);

// --- Vue Global Error Handler ---
// This function will catch any unhandled errors from within Vue components.
app.config.errorHandler = (err, instance, info) => {
  // Log the error to the console for developers
  console.error("Unhandled Vue error:", err);
  console.error("Occurred in component:", instance ? instance.$.type.name : 'Unknown');
  console.error("Vue-specific info:", info);

  // In a real production environment, you would send this error
  // to a tracking service like Sentry, LogRocket, or Datadog.
  // Example: Sentry.captureException(err);

  // Optionally, you could use a global store to show a user-facing
  // "An unexpected error occurred" message.
  const notificationStore = useNotificationStore(); // Assumes Pinia is available
  notificationStore.showNotification("Une erreur inattendue est survenue.", "error");
};


// 2. Create the Pinia instance for state management
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)

// 3. Use Pinia and the Router
app.use(pinia);
app.use(router);

// 4. Mount the application to the DOM
app.mount('#app');
