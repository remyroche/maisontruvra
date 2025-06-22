import B2BPortal from './components/B2BPortal.vue';
import apiClient from '../../js/api-client'; // Assuming a shared API client

document.addEventListener('DOMContentLoaded', () => {
  const portalAppElement = document.getElementById('b2b-portal-app');

  if (portalAppElement) {
    const app = Vue.createApp(B2BPortal);
    
    // Provide the API client to all child components
    app.provide('apiClient', apiClient);

    app.mount(portalAppElement);
    console.log('B2B Portal Vue App Mounted.');
  } else {
    console.error('Mounting element for B2B Portal App (#b2b-portal-app) not found.');
  }
});
