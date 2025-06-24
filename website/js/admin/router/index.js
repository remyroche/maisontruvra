/*
 * FILENAME: website/js/admin/router/index.js
 * DESCRIPTION: Vue Router configuration for the Admin Portal.
 *
 * UPDATED: Added the route for the new 'Manage Products' page.
 */
import { createRouter, createWebHistory } from 'vue-router';
import { useAdminAuthStore } from '../../stores/adminAuth';

// Import Admin Views
import AdminDashboardView from '../views/AdminDashboardView.vue';
import ManageUsersView from '../views/ManageUsersView.vue';
import ManageProductsView from '../views/ManageProductsView.vue'; // <-- New Import

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
    meta: { requiresAuth: true, requiredPermission: 'manage_users' }
  },
  // --- New Route ---
  {
    path: '/admin/products',
    name: 'AdminManageProducts',
    component: ManageProductsView,
    meta: { requiresAuth: true, requiredPermission: 'manage_products' }
  },
  {
    path: '/admin/:pathMatch(.*)*',
    redirect: '/admin'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Security Navigation Guard (no changes needed)
router.beforeEach(async (to, from, next) => {
  const authStore = useAdminAuthStore();
  if (authStore.adminUser === null) {
    await authStore.checkAuthStatus();
  }
  const isAuthenticated = authStore.isAuthenticated;
  const userPermissions = authStore.permissions;
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiredPermission = to.meta.requiredPermission;

  if (requiresAuth && !isAuthenticated) {
    window.location.href = '/admin/login';
  } else if (requiredPermission && !userPermissions.includes(requiredPermission)) {
    console.warn(`Access denied to ${to.path}. Missing permission: ${requiredPermission}`);
    next({ name: 'AdminDashboard' });
  } else {
    next();
  }
});

export default router;
