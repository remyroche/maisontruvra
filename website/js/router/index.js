import { createRouter, createWebHistory } from 'vue-router';
import Home from '../vue/views/Home.vue'; // The homepage can be loaded eagerly

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/shop',
    name: 'Shop',
    // LAZY LOADING: This component is only loaded when the user visits /shop
    component: () => import('../vue/views/ShopView.vue'),
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    // LAZY LOADING
    component: () => import('../vue/views/ProductDetailView.vue'),
    props: true,
  },
  {
    path: '/le-journal',
    name: 'Journal',
    // LAZY LOADING: The blog list code is split into its own file
    component: () => import('../vue/views/JournalView.vue'),
  },
  {
    path: '/le-journal/:slug',
    name: 'Article',
     // LAZY LOADING: Each article also uses a lazy-loaded component
    component: () => import('../vue/views/ArticleView.vue'),
    props: true,
  },
  {
    path: '/account',
    name: 'Account',
     // LAZY LOADING
    component: () => import('../vue/views/AccountView.vue'),
    meta: { requiresAuth: true }
  },
  // Add other B2C routes here
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// Add navigation guards for authentication if needed
// router.beforeEach((to, from, next) => { ... });

export default router;
