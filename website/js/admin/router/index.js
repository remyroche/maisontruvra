/*
 * FILENAME: website/js/admin/router/index.js
 * DESCRIPTION: Vue Router configuration for the Admin Portal.
 *
 * UPDATED: Added all remaining routes for the admin panel.
 */
import { createRouter, createWebHistory } from 'vue-router';
import { useAdminAuthStore } from '../../stores/adminAuth';

// Import all views
import AdminDashboardView from '../views/AdminDashboardView.vue';
import ManageUsersView from '../views/ManageUsersView.vue';
import ManageProductsView from '../views/ManageProductsView.vue';
import ManageOrdersView from '../views/ManageOrdersView.vue';
import ManageCategoriesView from '../views/ManageCategoriesView.vue';
import ManageCollectionsView from '../views/ManageCollectionsView.vue';
import ManageBlogView from '../views/ManageBlogView.vue';
import ManageReviewsView from '../views/ManageReviewsView.vue';
import ManageB2BView from '../views/ManageB2BView.vue';
import ManageLoyaltyView from '../views/ManageLoyaltyView.vue';
import SiteSettingsView from '../views/SiteSettingsView.vue';
import AuditLogView from '../views/AuditLogView.vue';
import AdminProfileView from '../views/AdminProfileView.vue';
import ManageAssetsView from '../views/ManageAssetsView.vue';

const routes = [
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboardView, meta: { requiresAuth: true } },
  { path: '/admin/profile', name: 'AdminProfile', component: AdminProfileView, meta: { requiresAuth: true } },
  // User Management
  { path: '/admin/users', name: 'AdminManageUsers', component: ManageUsersView, meta: { requiresAuth: true, requiredPermission: 'manage_users' } },
  // Product Management
  { path: '/admin/products', name: 'AdminManageProducts', component: ManageProductsView, meta: { requiresAuth: true, requiredPermission: 'manage_products' } },
  { path: '/admin/categories', name: 'AdminManageCategories', component: ManageCategoriesView, meta: { requiresAuth: true, requiredPermission: 'manage_categories' } },
  { path: '/admin/collections', name: 'AdminManageCollections', component: ManageCollectionsView, meta: { requiresAuth: true, requiredPermission: 'manage_collections' } },
  { path: '/admin/reviews', name: 'AdminManageReviews', component: ManageReviewsView, meta: { requiresAuth: true, requiredPermission: 'manage_reviews' } },
  // Order Management
  { path: '/admin/orders', name: 'AdminManageOrders', component: ManageOrdersView, meta: { requiresAuth: true, requiredPermission: 'manage_orders' } },
  // B2B
  { path: '/admin/b2b', name: 'AdminManageB2B', component: ManageB2BView, meta: { requiresAuth: true, requiredPermission: 'manage_b2b' } },
  // Marketing
  { path: '/admin/blog', name: 'AdminManageBlog', component: ManageBlogView, meta: { requiresAuth: true, requiredPermission: 'manage_blog' } },
  { path: '/admin/loyalty', name: 'AdminManageLoyalty', component: ManageLoyaltyView, meta: { requiresAuth: true, requiredPermission: 'manage_loyalty' } },
  // Site & System
  { path: '/admin/assets', name: 'AdminManageAssets', component: ManageAssetsView, meta: { requiresAuth: true, requiredPermission: 'manage_assets' } },
  { path: '/admin/settings', name: 'AdminSiteSettings', component: SiteSettingsView, meta: { requiresAuth: true, requiredPermission: 'manage_site_settings' } },
  { path: '/admin/audit-log', name: 'AdminAuditLog', component: AuditLogView, meta: { requiresAuth: true, requiredPermission: 'view_audit_log' } },
  // Catch-all
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
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    window.location.href = '/admin/login';
  } else if (to.meta.requiredPermission && !authStore.permissions.includes(to.meta.requiredPermission)) {
    next({ name: 'AdminDashboard' });
  } else {
    next();
  }
});

export default router;
