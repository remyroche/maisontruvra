import { createApp } from 'vue';
import { createPinia } from 'pinia';
import B2BDashboard from '../../js/vue/components/B2BDashboard.vue';

const dashboardElement = document.getElementById('b2b-dashboard');

if (dashboardElement) {
  const pinia = createPinia();
  const app = createApp(B2BDashboard);

  app.use(pinia);
  app.mount('#b2b-dashboard');
}

// Re-initialize i18n for the dynamic content
import i18n from '../../js/i18n.js';
document.addEventListener('DOMContentLoaded', () => {
    const lang = localStorage.getItem('language') || 'fr';
    i18n.init(lang);
});
