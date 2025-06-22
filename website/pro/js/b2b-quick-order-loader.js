import { createApp } from 'vue';
import { createPinia } from 'pinia';
import B2BQuickOrderForm from '../../js/vue/components/B2BQuickOrderForm.vue';

const quickOrderElement = document.getElementById('b2b-quick-order-form');

if (quickOrderElement) {
  const pinia = createPinia();
  const app = createApp(B2BQuickOrderForm);

  app.use(pinia);
  app.mount('#b2b-quick-order-form');
}

// Re-initialize i18n for the dynamic content
import i18n from '../../js/i18n.js';
document.addEventListener('DOMContentLoaded', () => {
    const lang = localStorage.getItem('language') || 'fr';
    i18n.init(lang);
});
