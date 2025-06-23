// website/source/js/main.js
import { createApp } from 'vue';
import App from '@/vue/App.vue';
import router from './router/index.js';
import '@/css/public.css'; // Import Tailwind CSS entry file
import { createPinia } from 'pinia';
import { defineRule, configure } from 'vee-validate';
import { required, email, min, confirmed, max } from '@vee-validate/rules';
import { localize } from '@vee-validate/i18n';
import { sanitizeHTML } from './security.js';

// --- VeeValidate Global Configuration ---
// Define validation rules globally
defineRule('required', required);
defineRule('email', email);
defineRule('min', min);
defineRule('max', max);
defineRule('confirmed', confirmed);

// Configure default error messages and validation triggers
configure({
  generateMessage: localize('fr', {
    messages: {
      required: 'Ce champ est requis',
      email: 'Veuillez saisir une adresse email valide',
      min: 'Ce champ doit contenir au moins {length} caractères',
      max: 'Ce champ ne peut pas dépasser {length} caractères',
      confirmed: 'Les mots de passe ne correspondent pas'
    }
  }),
  validateOnBlur: true,      // Validate when a user leaves a field
  validateOnChange: true,    // Validate when the value changes
  validateOnInput: true,     // Validate on every keystroke
});
// --- End VeeValidate Configuration ---

// 1. Create the Pinia instance for state management
const pinia = createPinia();

// 2. Create the Vue application instance
const app = createApp(App);

// 3. Use Pinia and the Router
app.use(pinia);
app.use(router);

// 4. Mount the application to the DOM
app.mount('#app');