import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../vue/views/HomeView.vue'),
  },
  {
    path: '/notre-maison',
    name: 'NotreMaison',
    component: () => import('../vue/views/NotreMaisonView.vue'),
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../vue/views/SearchView.vue'),
    // Props are passed from the URL query string
    props: route => ({ query: route.query.q })
  },
  {
    path: '/charte-qualite',
    name: 'CharteQualite',
    component: () => import('../vue/views/CharteQualiteView.vue'),
  },
  {
    path: '/politique-confidentialite',
    name: 'PolitiqueConfidentialite',
    component: () => import('../vue/views/PolitiqueConfidentialiteView.vue'),
  },
  {
    path: '/professionnels',
    name: 'Professionnels',
    component: () => import('../vue/views/ProfessionnelsView.vue'),
  },
  {
    path: '/shop',
    name: 'Shop',
    component: () => import('../vue/views/ShopView.vue'),
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../vue/views/ProductDetailView.vue'),
    props: true,
  },
  {
    path: '/le-journal',
    name: 'Journal',
    component: () => import('../vue/views/JournalView.vue'),
  },
  {
    path: '/le-journal/:slug',
    name: 'Article',
    component: () => import('../vue/views/ArticleView.vue'),
    props: true,
  },
  {
    path: '/account',
    name: 'Account',
    component: () => import('../vue/views/AccountView.vue'),
    meta: { requiresAuth: true }
  },
   // Catch-all route for 404 Not Found
   {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../vue/views/NotFoundView.vue'),
   }
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

export default router;
