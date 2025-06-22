// website/source/js/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/js/stores/auth.js';
import { useUserStore } from '@/js/stores/user.js';

// Lazy load components for better performance
const ShopApp = () => import('@/vue/ShopApp.vue');
const ProductCatalogue = () => import('@/vue/components/shop/ProductCatalogue.vue');
const ProductDetail = () => import('@/vue/components/shop/ProductDetail.vue');
const ShoppingCart = () => import('@/vue/components/shop/ShoppingCart.vue');
const UserProfile = () => import('@/vue/components/shop/UserProfile.vue');
const AuthPortal = () => import('@/vue/components/AuthPortal.vue');
const B2BPortal = () => import('@/vue/components/B2BPortal.vue');

const routes = [
    // B2C Customer-Facing Routes
    {
        path: '/',
        component: ShopApp,
        children: [
            { path: '', name: 'home', redirect: '/nos-produits' },
            { path: 'nos-produits', name: 'catalogue', component: ProductCatalogue },
            { path: 'produit/:slug', name: 'product-detail', component: ProductDetail, props: true },
            { path: 'panier', name: 'cart', component: ShoppingCart },
            { path: 'compte', name: 'profile', component: UserProfile, meta: { requiresAuth: true, isB2C: true } },
        ]
    },
    // B2B Professional Routes
    {
        path: '/pro',
        children: [
            { path: '', redirect: '/pro/login' },
            { path: 'login', name: 'pro-login', component: AuthPortal },
            { path: 'dashboard', name: 'pro-dashboard', component: B2BPortal, meta: { requiresAuth: true, isB2B: true } }
        ]
    },
    // Redirect legacy URLs
    { path: '/professionnels.html', redirect: '/pro/login' },
    { path: '/pro/professionnels.html', redirect: '/pro/login' },
    { path: '/pro/interactive_vue.html', redirect: '/pro/dashboard' },
    { path: '/nos-produits.html', redirect: '/nos-produits' },
    { path: '/panier.html', redirect: '/panier' },
    { path: '/compte.html', redirect: '/compte' },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Navigation Guard to protect routes
router.beforeEach(async (to, from, next) => {
    if (to.meta.requiresAuth) {
        const store = to.meta.isB2B ? useAuthStore() : useUserStore();
        
        // Check auth status if we haven't already
        if (!store.isAuthenticated) {
            await store.fetchProfile(); // Assumes both B2C and B2B stores have a `fetchProfile` action
        }
        
        if (store.isAuthenticated) {
            next();
        } else {
            // Redirect to appropriate login page
            const loginRoute = to.meta.isB2B ? { name: 'pro-login' } : { name: 'home' }; // Redirect B2C to homepage
            next(loginRoute);
        }
    } else {
        next();
    }
});

export default router;
