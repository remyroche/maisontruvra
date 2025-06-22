// website/source/js/main.js
import { createApp } from 'vue';
import App from '@/vue/App.vue';
import router from './router/index.js';
import '@/css/public.css'; // Import Tailwind CSS entry file
import { createPinia } from 'pinia';
import { defineRule, configure } from 'vee-validate';
import { required, email, min, confirmed } from '@vee-validate/rules';

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

// 3. Use Pinia and the Router
app.use(pinia);
app.use(router);

// 4. Mount the application to the DOM
app.mount('#app');
