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
  { path: '/blog', name: 'ManageBlog', component: ManageBlogView, meta: { requiresAuth: true, roles: ['Admin', 'Manager', 'Editor'] } },

  // Site & System
  { path: '/admin/assets', name: 'AdminManageAssets', component: ManageAssetsView, meta: { requiresAuth: true, requiredPermission: 'manage_assets' } },
  { path: '/admin/pos', name: 'AdminPOS', component: ManagePosView, meta: { requiresAuth: true, requiredPermission: 'use_pos' } },


  // Critical pages with role restrictions
  { 
    path: '/audit-log', 
    name: 'AuditLog', 
    component: AuditLogView, 
    meta: { requiredRoles: ['Admin', 'Manager', 'Dev'] } 
  },
  { 
    path: '/site-settings', 
    name: 'SiteSettings', 
    component: SiteSettingsView, 
    meta: { requiredRoles: ['Admin', 'Manager', 'Dev'] } 
  },
  { 
    path: '/manage-sessions', 
    name: 'ManageSessions', 
    component: ManageSessionsView, 
    meta: { requiredRoles: ['Admin', 'Manager', 'Dev'] } 
  },
  { 
    path: '/manage-roles', 
    name: 'ManageRoles', 
    component: ManageRolesView, 
    meta: { requiredRoles: ['Admin', 'Manager', 'Dev'] } 
  },
  
  // Catch-all
  { path: '/admin/:pathMatch(.*)*', redirect: '/admin' }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const adminAuthStore = useAdminAuthStore();
  const requiresRoles = to.meta.requiredRoles;

  // If the route has requiredRoles meta field
  if (requiresRoles) {
    // Check if the user is authenticated
    if (!adminAuthStore.isAuthenticated) {
      // If not authenticated, redirect to admin login page
      console.log('Redirecting to login: Not authenticated for roles-protected route.');
      next({ path: '/admin/login' });
    } else {
      // If authenticated, check if the user's role is authorized
      const userRole = adminAuthStore.user?.role; // Assuming user.role is a string like 'Admin', 'Manager', 'Staff'
      
      if (userRole && requiresRoles.includes(userRole)) {
        // Role is authorized, proceed to the route
        next();
      } else {
        // Role is not authorized, redirect to admin dashboard
        console.warn(`Unauthorized access attempt for ${to.path}. User role: ${userRole}. Required roles: ${requiresRoles.join(', ')}`);
        // You might want to show a more specific "access denied" page or message
        next({ path: '/admin' }); 
      }
    }
  } else {
    // No specific roles required, proceed to the route
    next();
  }
});

export default router;
