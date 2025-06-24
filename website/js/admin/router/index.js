/*
 * FILENAME: website/js/admin/router/index.js
 * DESCRIPTION: Vue Router configuration for the Admin Portal.
 *
 * This file defines all the client-side routes for the admin SPA.
 * It includes a navigation guard (`beforeEach`) to ensure that only authenticated
 * admin users can access the portal, redirecting them to the login page if not.
 * This is a critical client-side security measure.
 */
import { createRouter, createWebHistory } from 'vue-router';
import { useAdminAuthStore } from '../../stores/adminAuth';

// Import Admin Views
import AdminDashboardView from '../views/AdminDashboardView.vue';
import ManageUsersView from '../views/ManageUsersView.vue';
// Future views to be added here
// import ManageProductsView from '../views/ManageProductsView.vue';
// import ManageOrdersView from '../views/ManageOrdersView.vue';

const routes = [
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users',
    name: 'AdminManageUsers',
    component: ManageUsersView,
    meta: { requiresAuth: true, requiredPermission: 'manage_users' } // Example of permission-based routing
  },
  // Add other admin routes here
  // {
  //   path: '/admin/products',
  //   name: 'AdminManageProducts',
  //   component: ManageProductsView,
  //   meta: { requiresAuth: true, requiredPermission: 'manage_products' }
  // },
  {
    // A catch-all route for the admin SPA could be added here if needed
    path: '/admin/:pathMatch(.*)*',
    redirect: '/admin'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// --- Security: Navigation Guard ---
// This guard runs before each navigation, checking for authentication and permissions.
router.beforeEach(async (to, from, next) => {
  const authStore = useAdminAuthStore();

  // Check if the user's auth status is known. If not, fetch it.
  if (authStore.adminUser === null) {
    await authStore.checkAuthStatus();
  }

  const isAuthenticated = authStore.isAuthenticated;
  const userPermissions = authStore.permissions;

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiredPermission = to.meta.requiredPermission;

  if (requiresAuth && !isAuthenticated) {
    // User is not authenticated, redirect to the main admin login page.
    // The server will handle rendering the login page.
    window.location.href = '/admin/login';
  } else if (requiredPermission && !userPermissions.includes(requiredPermission)) {
    // User is authenticated but lacks specific permissions.
    // Redirect to a 'Not Authorized' page or the admin dashboard.
    console.warn(`Access denied to ${to.path}. Missing permission: ${requiredPermission}`);
    next({ name: 'AdminDashboard' }); // Or a dedicated '403 Forbidden' view
  }
  else {
    // User is authenticated and has permissions, or the route doesn't require auth.
    next();
  }
});

export default router;
