/*
 * FILENAME: website/admin/main-admin.js
 * DESCRIPTION: The main entry point for the Admin Portal Vue.js application.
 *
 * This file initializes the Vue app, creates the Pinia state management instance,
 * sets up the Vue Router, and mounts the root component (`AdminApp.vue`) to the
 * DOM element '#admin-app' in `website/admin/index.html`.
 */
import { createApp } from 'vue';
import { createPinia } from 'pinia';

import AdminApp from '../js/admin/AdminApp.vue';
import router from '../js/admin/router';
import { useAdminAuthStore } from '../js/stores/adminAuth';

// 1. Initialize Vue App
const app = createApp(AdminApp);

// 2. Install Pinia for state management
app.use(createPinia());

// --- Initial Authentication Check ---
// Before mounting the app, we check the user's authentication status.
// This is crucial to prevent rendering protected content before the user is verified.
const authStore = useAdminAuthStore();
authStore.checkAuthStatus().then(() => {
    // 3. Install Vue Router
    app.use(router);

    // 4. Mount the app to the DOM
    app.mount('#admin-app');
});
