<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Unified Header with Section Selector -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Top Navigation Bar -->
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <router-link to="/" class="flex-shrink-0">
              <img class="h-8 w-auto" src="/logo.svg" alt="Maison Truvra" />
            </router-link>
          </div>

          <!-- Section Selector -->
          <div v-if="!isAdminLoginPage" class="hidden md:flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              @click="switchSection('b2c')"
              :class="[
                'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
                currentSection === 'b2c' 
                  ? 'bg-white text-brand-burgundy shadow-sm' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-white/50'
              ]"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
                <span>Boutique</span>
              </div>
            </button>
            
            <button
              @click="switchSection('b2b')"
              :class="[
                'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
                currentSection === 'b2b' 
                  ? 'bg-white text-brand-burgundy shadow-sm' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-white/50'
              ]"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span>Professionnels</span>
              </div>
            </button>
            
            <button
              @click="switchSection('admin')"
              :class="[
                'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
                currentSection === 'admin' 
                  ? 'bg-white text-brand-burgundy shadow-sm' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-white/50'
              ]"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>Administration</span>
              </div>
            </button>
          </div>

          <!-- Right side actions -->
          <div class="flex items-center space-x-4">
            <!-- Language Switcher -->
            <div class="relative">
              <button @click="toggleLanguage" class="p-2 rounded-full text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-burgundy">
                <span class="text-sm font-medium">{{ currentLanguage.toUpperCase() }}</span>
              </button>
            </div>

            <!-- Search Button -->
            <button @click="openSearch" class="p-2 rounded-full text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-burgundy">
              <span class="sr-only">Search</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>

            <!-- User Account -->
            <router-link to="/account" class="p-2 rounded-full text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-burgundy">
              <span class="sr-only">View account</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </router-link>

            <!-- Cart Icon -->
            <router-link to="/cart" class="p-2 rounded-full text-gray-400 hover:text-gray-600 relative">
              <span class="sr-only">View cart</span>
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              <span v-if="cartCount > 0" class="absolute -top-1 -right-1 block h-4 w-4 rounded-full bg-brand-burgundy text-white text-xs flex items-center justify-center">{{ cartCount }}</span>
            </router-link>
          </div>
        </div>

        <!-- Section-specific Navigation -->
        <div v-if="currentSection !== 'admin' && !isAdminLoginPage" class="border-t border-gray-200">
          <nav class="flex space-x-8 py-4">
            <router-link 
              v-for="item in sectionNavigation" 
              :key="item.name" 
              :to="item.href"
              class="text-gray-500 hover:text-brand-burgundy px-3 py-2 rounded-md text-sm font-medium transition-colors"
              active-class="text-brand-burgundy bg-brand-cream"
            >
              {{ $t(item.name) }}
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1">
      <!-- B2C Section -->
      <div v-if="currentSection === 'b2c'" class="min-h-screen">
        <router-view />
      </div>

      <!-- B2B Section -->
      <div v-if="currentSection === 'b2b'" class="min-h-screen bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div class="bg-white rounded-lg shadow-sm border">
            <div class="px-6 py-4 border-b border-gray-200">
              <h1 class="text-2xl font-bold text-brand-dark-brown">Espace Professionnel</h1>
              <p class="text-gray-600 mt-1">Gérez vos commandes, demandes de devis et accédez à nos services B2B</p>
            </div>
            <div class="p-6">
              <router-view />
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Login Page -->
      <div v-if="isAdminLoginPage" class="min-h-screen">
        <router-view />
      </div>

      <!-- Admin Section -->
      <div v-if="currentSection === 'admin' && !isAdminLoginPage" class="flex h-screen bg-gray-100">
        <!-- Admin Sidebar -->
        <aside class="w-64 bg-gray-800 text-white flex-shrink-0">
          <div class="p-4 text-lg font-semibold border-b border-gray-700">
            <div class="flex items-center space-x-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Administration</span>
            </div>
          </div>
          <nav class="mt-4">
            <ul>
              <li v-for="item in adminNavItems" :key="item.name">
                <router-link 
                  :to="item.path" 
                  class="flex items-center p-4 hover:bg-gray-700 transition-colors"
                  active-class="bg-gray-700"
                >
                  <component :is="item.icon" class="h-5 w-5 mr-3" />
                  <span class="text-sm">{{ item.name }}</span>
                </router-link>
              </li>
            </ul>
          </nav>
        </aside>

        <!-- Admin Main Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <header class="bg-white shadow-sm p-4 flex justify-between items-center">
            <h1 class="text-xl font-bold text-brand-dark-brown">Tableau de bord</h1>
            <div class="flex items-center space-x-4">
              <router-link to="/admin/profile" class="text-gray-600 hover:text-brand-burgundy">Profil</router-link>
              <button @click="logout" class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition-colors">
                Déconnexion
              </button>
            </div>
          </header>
          <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
            <router-view />
          </main>
        </div>
      </div>
    </main>

    <!-- Footer for B2C section only -->
    <Footer v-if="currentSection === 'b2c'" />

    <!-- Global Components -->
    <Notification />
    <CookieBanner />
    <SearchOverlay />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useCartStore } from '@/stores/cart';
import { useUserStore } from '@/stores/user';
import { useAdminAuthStore } from '@/stores/adminAuth';
import { useI18n } from 'vue-i18n';
import Notification from '@/components/ui/Notification.vue';
import CookieBanner from '@/components/layout/CookieBanner.vue';
import SearchOverlay from '@/components/search/SearchOverlay.vue';
import Footer from '@/components/layout/Footer.vue';

// Icons for admin navigation
import {
  ChartBarIcon,
  UsersIcon,
  ShoppingBagIcon,
  TagIcon,
  CubeIcon,
  CollectionIcon,
  TruckIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  ChatAlt2Icon,
  NewspaperIcon,
  SparklesIcon,
  CogIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  DocumentReportIcon,
  ClockIcon,
  KeyIcon,
  ViewGridIcon,
  QrcodeIcon,
  TerminalIcon,
  GiftIcon,
  TrashIcon,
  LightBulbIcon,
} from '@heroicons/vue/outline';

const router = useRouter();
const route = useRoute();
const { t, locale } = useI18n();

const cartStore = useCartStore();
const userStore = useUserStore();
const adminAuthStore = useAdminAuthStore();

// Current section state
const currentSection = ref('b2c');

// Check if we're on admin login page
const isAdminLoginPage = computed(() => route.path === '/admin/login');

// Computed properties
const cartCount = computed(() => cartStore.itemCount);
const currentLanguage = computed(() => locale.value);

// Navigation items for each section
const sectionNavigation = computed(() => {
  if (currentSection.value === 'b2c') {
    return [
      { name: 'header.shop', href: '/shop' },
      { name: 'header.journal', href: '/le-journal' },
      { name: 'header.about', href: '/notre-maison' },
      { name: 'header.professionals', href: '/professionnels' },
    ];
  } else if (currentSection.value === 'b2b') {
    return [
      { name: 'B2B Dashboard', href: '/pro/dashboard' },
      { name: 'Request Quote', href: '/pro/request-quote' },
      { name: 'My Quotes', href: '/pro/my-quotes' },
      { name: 'B2B Orders', href: '/pro/orders' },
    ];
  }
  return [];
});

const adminNavItems = [
  { name: 'Dashboard', path: '/admin', icon: ChartBarIcon },
  { name: 'Users', path: '/admin/users', icon: UsersIcon },
  { name: 'B2B', path: '/admin/b2b', icon: UserGroupIcon },
  { name: 'Orders', path: '/admin/orders', icon: ShoppingBagIcon },
  { name: 'Products', path: '/admin/products', icon: CubeIcon },
  { name: 'Categories', path: '/admin/categories', icon: TagIcon },
  { name: 'Collections', path: '/admin/collections', icon: CollectionIcon },
  { name: 'Inventory', path: '/admin/inventory', icon: ViewGridIcon },
  { name: 'Delivery', path: '/admin/delivery', icon: TruckIcon },
  { name: 'Discounts', path: '/admin/discounts', icon: CurrencyDollarIcon },
  { name: 'Invoices', path: '/admin/invoices', icon: DocumentTextIcon },
  { name: 'Quotes', path: '/admin/quotes', icon: ChatAlt2Icon },
  { name: 'Reviews', path: '/admin/reviews', icon: ChatAlt2Icon },
  { name: 'Blog', path: '/admin/blog', icon: NewspaperIcon },
  { name: 'Loyalty', path: '/admin/loyalty', icon: SparklesIcon },
  { name: 'Newsletter', path: '/admin/newsletter', icon: GiftIcon },
  { name: 'Recommendations', path: '/admin/recommendations', icon: LightBulbIcon },
  { name: 'Assets', path: '/admin/assets', icon: DocumentReportIcon },
  { name: 'Passports', path: '/admin/passports', icon: QrcodeIcon },
  { name: 'POS', path: '/admin/pos', icon: TerminalIcon },
  { name: 'Sessions', path: '/admin/sessions', icon: ClockIcon },
  { name: 'Roles', path: '/admin/roles', icon: KeyIcon },
  { name: 'Site Settings', path: '/admin/site-settings', icon: CogIcon },
  { name: 'Audit Log', path: '/admin/audit-log', icon: ShieldCheckIcon },
  { name: 'Recycling Bin', path: '/admin/recycling-bin', icon: TrashIcon },
];

// Methods
const switchSection = (section) => {
  currentSection.value = section;
  
  // Navigate to appropriate default route for each section
  switch (section) {
    case 'b2c':
      router.push('/');
      break;
    case 'b2b':
      router.push('/pro/dashboard');
      break;
    case 'admin':
      // Check if admin is authenticated
      if (adminAuthStore.isAuthenticated) {
        router.push('/admin');
      } else {
        router.push({ name: 'AdminLogin' });
      }
      break;
  }
};

const toggleLanguage = () => {
  const newLocale = currentLanguage.value === 'fr' ? 'en' : 'fr';
  locale.value = newLocale;
};

const openSearch = () => {
  console.log('Open search');
};

const logout = async () => {
  if (currentSection.value === 'admin') {
    await adminAuthStore.logout();
    router.push({ name: 'AdminLogin' });
  } else {
    await userStore.logout();
    router.push('/');
  }
};

// Determine current section based on route
const determineCurrentSection = () => {
  const path = route.path;
  if (path.startsWith('/admin')) {
    currentSection.value = 'admin';
  } else if (path.startsWith('/pro')) {
    currentSection.value = 'b2b';
  } else {
    currentSection.value = 'b2c';
  }
};

// Watch route changes to update section
router.afterEach(() => {
  determineCurrentSection();
});

// Initialize
onMounted(async () => {
  determineCurrentSection();
  
  // Check authentication status
  if (userStore.isLoggedIn === null) {
    await userStore.checkAuthStatus();
  }
  
  if (adminAuthStore.user === null) {
    await adminAuthStore.checkAuth();
  }
});
</script>

<style scoped>
.router-link-active {
  @apply bg-gray-700;
}
</style>