/*
 * FILENAME: website/js/admin/router/index.js
 * DESCRIPTION: Vue Router configuration for the Admin Portal.
 *
 * UPDATED: Added the route for the new 'Manage Categories' page.
 */
import { createRouter, createWebHistory } from 'vue-router';
import { useAdminAuthStore } from '../../stores/adminAuth';

import AdminDashboardView from '../views/AdminDashboardView.vue';
import ManageUsersView from '../views/ManageUsersView.vue';
import ManageProductsView from '../views/ManageProductsView.vue';
import ManageOrdersView from '../views/ManageOrdersView.vue';
import ManageCategoriesView from '../views/ManageCategoriesView.vue'; // <-- New Import

const routes = [
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboardView, meta: { requiresAuth: true } },
  { path: '/admin/users', name: 'AdminManageUsers', component: ManageUsersView, meta: { requiresAuth: true, requiredPermission: 'manage_users' } },
  { path: '/admin/products', name: 'AdminManageProducts', component: ManageProductsView, meta: { requiresAuth: true, requiredPermission: 'manage_products' } },
  { path: '/admin/orders', name: 'AdminManageOrders', component: ManageOrdersView, meta: { requiresAuth: true, requiredPermission: 'manage_orders' } },
  // --- New Route ---
  {
    path: '/admin/categories',
    name: 'AdminManageCategories',
    component: ManageCategoriesView,
    meta: { requiresAuth: true, requiredPermission: 'manage_categories' }
  },
  { path: '/admin/:pathMatch(.*)*', redirect: '/admin' }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Security Navigation Guard (no changes needed)
router.beforeEach(async (to, from, next) => {
  const authStore = useAdminAuthStore();
  if (authStore.adminUser === null) { await authStore.checkAuthStatus(); }
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
