import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import { defineRule, configure, Form, Field, ErrorMessage } from 'vee-validate';
import * as AllRules from '@vee-validate/rules';
import { localize, setLocale } from '@vee-validate/i18n';
import fr from '@vee-validate/i18n/dist/locale/fr.json';
import en from '@vee-validate/i18n/dist/locale/en.json';


import App from './App.vue';
import router from './router';
import i18n from './services/i18n'; // Import our custom i18n service

import './style.css';

// --- VeeValidate Configuration ---
// Define all validation rules globally
Object.keys(AllRules).forEach(rule => {
  defineRule(rule, AllRules[rule]);
});

// Configure VeeValidate to use localization
configure({
  generateMessage: localize({ fr, en }),
  validateOnInput: true, // Validate fields as the user types
});

// Set default locale for validation messages
setLocale('fr');

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate); // Add persistence to Pinia stores

app.use(pinia);
app.use(router);
app.use(i18n); // Use our custom i18n service

// Register VeeValidate components globally
app.component('VeeForm', Form);
app.component('VeeField', Field);
app.component('VeeErrorMessage', ErrorMessage);


app.mount('#app');
