import { createApp } from 'vue';
import { createPinia } from 'pinia';

// Import all B2B components
import B2BDashboard from '../../js/vue/components/B2BDashboard.vue';
import B2BLoyalty from '../../js/vue/components/B2BLoyalty.vue';
import B2BInvoices from '../../js/vue/components/B2BInvoices.vue';
import B2BProfile from '../../js/vue/components/B2BProfile.vue';

// A generic function to create and mount a Vue app
const mountApp = (component, elementId) => {
    const element = document.getElementById(elementId);
    if (element) {
        const pinia = createPinia();
        const app = createApp(component);
        app.use(pinia);
        app.mount(`#${elementId}`);
    }
};

// Mount all potential B2B portal apps on DOM content loaded
// This script will be included in each HTML file
document.addEventListener('DOMContentLoaded', () => {
    // On the dashboard page, this will find the element and mount the app
    mountApp(B2BDashboard, 'b2b-dashboard-app');
    
    // On the loyalty page, this will find the element and mount the app
    mountApp(B2BLoyalty, 'b2b-loyalty-app');
    
    // On the invoices page, this will find the element and mount the app
    mountApp(B2BInvoices, 'b2b-invoices-app');

    // On the profile page, this will find the element and mount the app
    mountApp(B2BProfile, 'b2b-profile-app');

    // Re-initialize i18n after mounting, if necessary
    if (window.i18n) {
        const lang = localStorage.getItem('language') || 'fr';
        window.i18n.init(lang);
    }
});
