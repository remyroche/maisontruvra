import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../stores/user';

// It's good practice to define lazy-loaded components for better performance
const HomeView = () => import('../vue/views/HomeView.vue');
const NotreMaisonView = () => import('../vue/views/NotreMaisonView.vue');
const SearchView = () => import('../vue/views/SearchView.vue');
const CharteQualiteView = () => import('../vue/views/CharteQualiteView.vue');
const PolitiqueConfidentialiteView = () => import('../vue/views/PolitiqueConfidentialiteView.vue');
const ProfessionnelsView = () => import('../vue/views/ProfessionnelsView.vue');
const FaqView = () => import('../vue/views/FaqView.vue');
const ShopView = () => import('../vue/views/ShopView.vue');
const ProductDetailView = () => import('../vue/views/ProductDetailView.vue');
const JournalView = () => import('../vue/views/JournalView.vue');
const ArticleView = () => import('../vue/views/ArticleView.vue');
const CheckoutView = () => import('../vue/views/CheckoutView.vue');
const AccountView = () => import('../vue/views/AccountView.vue');
const DashboardView = () => import('../vue/views/DashboardView.vue');
const RewardsView = () => import('../vue/views/RewardsView.vue');
const ReferralView = () => import('../vue/views/ReferralView.vue');
const NotFoundView = () => import('../vue/views/NotFoundView.vue');


const routes = [
  // --- Public Routes ---
  { path: '/', name: 'Home', component: HomeView },
  { path: '/shop', name: 'Shop', component: ShopView },
  { path: '/product/:id', name: 'ProductDetail', component: ProductDetailView, props: true },
  { path: '/le-journal', name: 'Journal', component: JournalView },
  { path: '/le-journal/:slug', name: 'Article', component: ArticleView, props: true },
  { path: '/checkout', name: 'Checkout', component: CheckoutView },
  
  // --- Informational Pages ---
  { path: '/notre-maison', name: 'NotreMaison', component: NotreMaisonView },
  { path: '/charte-qualite', name: 'CharteQualite', component: CharteQualiteView },
  { path: '/politique-confidentialite', name: 'PolitiqueConfidentialite', component: PolitiqueConfidentialiteView },
  { path: '/professionnels', name: 'Professionnels', component: ProfessionnelsView },
  { path: '/faq', name: 'FAQ', component: FaqView },

  // --- Search ---
  { path: '/search', name: 'Search', component: SearchView, props: route => ({ query: route.query.q }) },

  // --- Authenticated User Routes ---
  { 
    path: '/account', 
    component: AccountView, 
    meta: { requiresAuth: true },
    // Nested routes for the account section for a better structure
    children: [
        { path: '', name: 'Account', redirect: '/account/dashboard' }, // Default to dashboard
        { path: 'dashboard', name: 'Dashboard', component: DashboardView },
        { path: 'rewards', name: 'Rewards', component: RewardsView },
        { path: 'referrals', name: 'Referrals', component: ReferralView },
        // Add other account pages like 'orders', 'profile' etc. here
    ]
  },
  
  // --- Catch-all 404 Route ---
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
  }
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

// --- Navigation Guard ---
router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore();
    // Ensure auth status is checked before navigating
    if (userStore.isLoggedIn === null) {
        await userStore.checkAuthStatus();
    }
    const isAuthenticated = userStore.isLoggedIn; 

    if (to.meta.requiresAuth && !isAuthenticated) {
        // Redirect to login page if route requires auth and user is not authenticated
        // You can also add a query param to redirect back after login: next({ name: 'Login', query: { redirect: to.fullPath } })
        next({ name: 'Home' }); 
    } else {
        next(); // Proceed to route
    }
});


export default router;
