// website/source/js/main.js
import { createApp } from 'vue';
import App from '@/vue/App.vue';
import router from './router/index.js';
import '@/css/public.css'; // Import Tailwind CSS entry file
import { createPinia } from 'pinia';
import { defineRule, configure } from 'vee-validate';
import { required, email, min, confirmed } from '@vee-validate/rules';
import * as Sentry from "@sentry/vue";

// --- VeeValidate Global Configuration ---
// Define validation rules globally
defineRule('required', required);
defineRule('email', email);
defineRule('min', min);
defineRule('confirmed', confirmed);

// Configure default error messages and validation triggers
configure({
  generateMessage: (context) => {
    const messages = {
      required: 'Ce champ est requis',
      email: 'Veuillez entrer une adresse email valide',
      min: `Ce champ doit contenir au moins ${context.rule.params[0]} caractères`,
      confirmed: 'Les mots de passe ne correspondent pas',
    };
    return messages[context.rule.name] || `Le champ ${context.field} est invalide`;
  },
  validateOnBlur: true,      // Validate when a user leaves a field
  validateOnChange: true,  // Validate when the value changes
  validateOnInput: true,     // Validate on every keystroke
});
// --- End VeeValidate Configuration ---


// 1. Create the Pinia instance for state management
const pinia = createPinia();

// 2. Create the Vue application instance
const app = createApp(App);

// --- Sentry Integration for Vue ---
// This is initialized only if the DSN is available in the environment variables.
if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [
      // Enables automatic capturing of promise rejections
      new Sentry.Replay(),
      // Enables performance monitoring
      Sentry.browserTracingIntegration({
        router, // Connect Sentry to the Vue router for route-based context
      }),
    ],
    // Performance Monitoring
    tracesSampleRate: 1.0, // Capture 100% of transactions. Lower this in high-traffic production.
    // Session Replay
    replaysSessionSampleRate: 0.1, // This percentage of sessions will be recorded.
    replaysOnErrorSampleRate: 1.0, // If a session encounters an error, L'enregistrement sera toujours effectué.
  });
}

// 3. Use Pinia and the Router
app.use(pinia);
app.use(createPinia());
app.use(router);


// 4. Mount the application to the DOM
app.mount('#app');
