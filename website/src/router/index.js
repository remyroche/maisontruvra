/*
 * FILENAME: website/src/router/index.js
 * DESCRIPTION: Vue Router configuration for the Admin Portal.
 * REFACTOR: Migrated to src/ and implemented lazy loading for all routes.
 */
import { createRouter, createWebHistory } from 'vue-router';
import { useAdminAuthStore } from '@/stores/adminAuth';
import { useUserStore } from '@/stores/user';

const routes = [
  // --- Public Routes ---
  { path: '/', name: 'Home', component: () => import('@/views/public/HomeView.vue') },
  { path: '/shop', name: 'Shop', component: () => import('@/views/public/ShopView.vue') },
  { path: '/product/:id', name: 'ProductDetail', component: () => import('@/views/public/ProductDetailView.vue'), props: true },
  { path: '/le-journal', name: 'Journal', component: () => import('@/views/public/JournalView.vue') },
  { path: '/le-journal/:slug', name: 'Article', component: () => import('@/views/public/ArticleView.vue'), props: true },
  { path: '/checkout', name: 'Checkout', component: () => import('@/views/public/CheckoutView.vue') },
  { path: '/order-confirmation/:id?', name: 'OrderConfirmation', component: () => import('@/views/public/OrderConfirmationView.vue'), props: true },
  { path: '/cart', name: 'ShoppingCart', component: () => import('../views/public/ShoppingCartView.vue'),
  },

  // --- Informational Pages ---
  { path: '/notre-maison', name: 'NotreMaison', component: () => import('@/views/public/NotreMaisonView.vue') },
  { path: '/charte-qualite', name: 'CharteQualite', component: () => import('@/views/public/CharteQualiteView.vue') },
  { path: '/politique-confidentialite', name: 'PolitiqueConfidentialite', component: () => import('@/views/public/PolitiqueConfidentialiteView.vue') },
  { path: '/professionnels', name: 'Professionnels', component: () => import('@/views/public/ProfessionnelsView.vue') },
  {
    path: '/faq',
    component: () => import('@/views/public/FaqView.vue'),
    children: [
      { path: '', redirect: { name: 'FaqB2C' } }, // Default to B2C
      { path: 'general', name: 'FaqB2C', component: () => import('@/components/faq/B2cFAQ.vue') },
      { path: 'professional', name: 'FaqB2B', component: () => import('@/components/faq/B2bFAQ.vue') }
    ]
  },

  // --- Search ---
  { path: '/search', name: 'Search', component: () => import('@/views/public/SearchView.vue'), props: route => ({ query: route.query.q }) },

  // --- Contact Pages ---
  { path: '/contact-b2c', name: 'ContactB2C', component: () => import('@/views/public/ContactB2C.vue') },
  { path: '/contact-b2b', name: 'ContactB2B', component: () => import('@/views/public/ContactB2B.vue') },

  // --- Authenticated User Routes ---
  { 
    path: '/account', 
    component: () => import('@/views/account/AccountView.vue'), 
    meta: { requiresAuth: true },
    children: [
        { path: '', name: 'Account', redirect: { name: 'Dashboard' } },
        { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/account/DashboardView.vue') },
        { path: 'rewards', name: 'Rewards', component: () => import('@/views/account/RewardsView.vue') },
        { path: 'referrals', name: 'Referrals', component: () => import('@/views/account/ReferralView.vue') },
    ]
  },

  // Core Admin
  { path: '/admin', name: 'AdminDashboard', component: () => import('@/views/admin/AdminDashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/admin/profile', name: 'AdminProfile', component: () => import('@/views/admin/AdminProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/admin/setup-mfa', name: 'SetupMfa', component: () => import('@/views/admin/SetupMfaView.vue'), meta: { requiresAuth: true } },
  
  // User Management
  { path: '/admin/users', name: 'AdminManageUsers', component: () => import('@/views/admin/ManageUsersView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_users' } },

  // Product Management
  { path: '/admin/products', name: 'AdminManageProducts', component: () => import('@/views/admin/ManageProductsView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_products' } },
  { path: '/admin/inventory', name: 'AdminManageInventory', component: () => import('@/views/admin/ManageInventoryView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_inventory' } },
  { path: '/admin/categories', name: 'AdminManageCategories', component: () => import('@/views/admin/ManageCategoriesView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_categories' } },
  { path: '/admin/collections', name: 'AdminManageCollections', component: () => import('@/views/admin/ManageCollectionsView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_collections' } },
  { path: '/admin/reviews', name: 'AdminManageReviews', component: () => import('@/views/admin/ManageReviewsView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_reviews' } },
  { path: '/admin/passports', name: 'AdminViewPassports', component: () => import('@/views/admin/ViewPassportsView.vue'), meta: { requiresAuth: true, requiredPermission: 'view_passports' } },

  // Order Management
  { path: '/admin/orders', name: 'AdminManageOrders', component: () => import('@/views/admin/ManageOrdersView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_orders' } },
  { path: '/admin/invoices', name: 'AdminManageInvoices', component: () => import('@/views/admin/ManageInvoicesView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_invoices' } },
  
  // B2B
  { path: '/admin/b2b', name: 'AdminManageB2B', component: () => import('@/views/admin/ManageB2BView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_b2b' } },
  { path: '/admin/quotes', name: 'AdminManageQuotes', component: () => import('@/views/admin/ManageQuotesView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_quotes' } },

  // Marketing
  { path: '/admin/blog', name: 'AdminManageBlog', component: () => import('@/views/admin/ManageBlogView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_blog' } },
  { path: '/admin/loyalty', name: 'AdminManageLoyalty', component: () => import('@/views/admin/ManageLoyaltyView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_loyalty' } },
  { path: '/admin/newsletter', name: 'AdminManageNewsletter', component: () => import('@/views/admin/ManageNewsletterView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_newsletter' } },
  
  // Site & System
  { path: '/admin/assets', name: 'AdminManageAssets', component: () => import('@/views/admin/ManageAssetsView.vue'), meta: { requiresAuth: true, requiredPermission: 'manage_assets' } },
  { path: '/admin/pos', name: 'AdminPOS', component: () => import('@/views/admin/ManagePosView.vue'), meta: { requiresAuth: true, requiredPermission: 'use_pos' } },

  // Critical pages with role restrictions
  { path: '/admin/audit-log', name: 'AuditLog', component: () => import('@/views/admin/AuditLogView.vue'), meta: { requiresAuth: true, requiredRoles: ['Admin', 'Manager', 'Dev'] } },
  { path: '/admin/site-settings', name: 'SiteSettings', component: () => import('@/views/admin/SiteSettingsView.vue'), meta: { requiresAuth: true, requiredRoles: ['Admin', 'Manager', 'Dev'] } },
  { path: '/admin/manage-sessions', name: 'ManageSessions', component: () => import('@/views/admin/ManageSessionsView.vue'), meta: { requiresAuth: true, requiredRoles: ['Admin', 'Manager', 'Dev'] } },
  { path: '/admin/manage-roles', name: 'ManageRoles', component: () => import('@/views/admin/ManageRolesView.vue'), meta: { requiresAuth: true, requiredRoles: ['Admin', 'Manager', 'Dev'] } },
  
  // Catch-all
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/public/NotFoundView.vue') }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0, behavior: 'smooth' };
    }
  },
});

router.beforeEach(async (to, from, next) => {
  const isAdminRoute = to.path.startsWith('/admin');

  if (isAdminRoute) {
    const adminAuthStore = useAdminAuthStore();
    if (adminAuthStore.user === null) {
      await adminAuthStore.checkAuth();
    }

    const { isAuthenticated, user } = adminAuthStore;
    const { requiresAuth, requiredPermission, requiredRoles } = to.meta;

    if ((requiresAuth || requiredPermission || requiredRoles) && !isAuthenticated) {
      return next({ path: '/admin/login' }); // Redirect to admin login
    }
    if (requiredRoles && (!user || !requiredRoles.includes(user.role))) {
      return next({ path: '/admin' }); // Redirect to admin dashboard
    }
    if (requiredPermission && (!user || !user.permissions?.includes(requiredPermission))) {
      return next({ path: '/admin' }); // Redirect to admin dashboard
    }
  } else {
    // Handle public routes
    const userStore = useUserStore();
    if (userStore.isLoggedIn === null) {
      await userStore.checkAuthStatus();
    }
    if (to.meta.requiresAuth && !userStore.isLoggedIn) {
      return next({ name: 'Home' }); // Or redirect to a public login page
    }
  }

  next();
});
 
export default router;
