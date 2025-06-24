/*
 * FILENAME: website/js/admin/router/index.js
 * DESCRIPTION: Vue Router configuration for the Admin Portal.
 * UPDATED: Added routes for all remaining admin pages.
 */
import { createRouter, createWebHistory } from 'vue-router';
import { useAdminAuthStore } from '../../stores/adminAuth';

// ... (existing view imports)
import ManageInventoryView from '../views/ManageInventoryView.vue';
import ManageNewsletterView from '../views/ManageNewsletterView.vue';
import ManagePosView from '../views/ManagePosView.vue';
import ManageQuotesView from '../views/ManageQuotesView.vue';
import ManageRolesView from '../views/ManageRolesView.vue';
import ManageSessionsView from '../views/ManageSessionsView.vue';
import SetupMfaView from '../views/SetupMfaView.vue';
import ViewPassportsView from '../views/ViewPassportsView.vue';


const routes = [
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboardView, meta: { requiresAuth: true } },
  { path: '/admin/profile', name: 'AdminProfile', component: AdminProfileView, meta: { requiresAuth: true } },
  { path: '/admin/setup-mfa', name: 'SetupMfa', component: SetupMfaView, meta: { requiresAuth: true } },
  
  // User Management
  { path: '/admin/users', name: 'AdminManageUsers', component: ManageUsersView, meta: { requiresAuth: true, requiredPermission: 'manage_users' } },
  { path: '/admin/roles', name: 'AdminManageRoles', component: ManageRolesView, meta: { requiresAuth: true, requiredPermission: 'manage_roles' } },
  { path: '/admin/sessions', name: 'AdminManageSessions', component: ManageSessionsView, meta: { requiresAuth: true, requiredPermission: 'manage_sessions' } },

  // Product Management
  { path: '/admin/products', name: 'AdminManageProducts', component: ManageProductsView, meta: { requiresAuth: true, requiredPermission: 'manage_products' } },
  { path: '/admin/inventory', name: 'AdminManageInventory', component: ManageInventoryView, meta: { requiresAuth: true, requiredPermission: 'manage_inventory' } },
  { path: '/admin/categories', name: 'AdminManageCategories', component: ManageCategoriesView, meta: { requiresAuth: true, requiredPermission: 'manage_categories' } },
  { path: '/admin/collections', name: 'AdminManageCollections', component: ManageCollectionsView, meta: { requiresAuth: true, requiredPermission: 'manage_collections' } },
  { path: '/admin/reviews', name: 'AdminManageReviews', component: ManageReviewsView, meta: { requiresAuth: true, requiredPermission: 'manage_reviews' } },
  { path: '/admin/passports', name: 'AdminViewPassports', component: ViewPassportsView, meta: { requiresAuth: true, requiredPermission: 'view_passports' } },

  // Order Management
  { path: '/admin/orders', name: 'AdminManageOrders', component: ManageOrdersView, meta: { requiresAuth: true, requiredPermission: 'manage_orders' } },
  { path: '/admin/invoices', name: 'AdminManageInvoices', component: ManageInvoicesView, meta: { requiresAuth: true, requiredPermission: 'manage_invoices' } },
  
  // B2B
  { path: '/admin/b2b', name: 'AdminManageB2B', component: ManageB2BView, meta: { requiresAuth: true, requiredPermission: 'manage_b2b' } },
  { path: '/admin/quotes', name: 'AdminManageQuotes', component: ManageQuotesView, meta: { requiresAuth: true, requiredPermission: 'manage_quotes' } },

  // Marketing
  { path: '/admin/blog', name: 'AdminManageBlog', component: ManageBlogView, meta: { requiresAuth: true, requiredPermission: 'manage_blog' } },
  { path: '/admin/loyalty', name: 'AdminManageLoyalty', component: ManageLoyaltyView, meta: { requiresAuth: true, requiredPermission: 'manage_loyalty' } },
  { path: '/admin/newsletter', name: 'AdminManageNewsletter', component: ManageNewsletterView, meta: { requiresAuth: true, requiredPermission: 'manage_newsletter' } },

  // Site & System
  { path: '/admin/assets', name: 'AdminManageAssets', component: ManageAssetsView, meta: { requiresAuth: true, requiredPermission: 'manage_assets' } },
  { path: '/admin/settings', name: 'AdminSiteSettings', component: SiteSettingsView, meta: { requiresAuth: true, requiredPermission: 'manage_site_settings' } },
  { path: '/admin/audit-log', name: 'AdminAuditLog', component: AuditLogView, meta: { requiresAuth: true, requiredPermission: 'view_audit_log' } },
  { path: '/admin/pos', name: 'AdminPOS', component: ManagePosView, meta: { requiresAuth: true, requiredPermission: 'use_pos' } },

  // Catch-all
  { path: '/admin/:pathMatch(.*)*', redirect: '/admin' }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAdminAuthStore();
  if (authStore.adminUser === null && !authStore.isLoading) { await authStore.checkAuthStatus(); }
  
  const isAuthenticated = authStore.isAuthenticated;
  const userPermissions = authStore.permissions || [];

  if (to.meta.requiresAuth && !isAuthenticated) {
    window.location.href = '/admin/login';
  } else if (to.meta.requiredPermission && !userPermissions.includes(to.meta.requiredPermission)) {
    console.warn(`Access denied to ${to.path}. Missing permission: ${to.meta.requiredPermission}`);
    next({ name: 'AdminDashboard' });
  } else {
    next();
  }
});

export default router;
