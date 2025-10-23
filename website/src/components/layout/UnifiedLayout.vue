<template>
  <div class="min-h-screen" :class="sectionBackgroundClass">
    <!-- Unified Header with Enhanced Section Selector -->
    <header class="sticky top-0 z-50" :class="headerClass">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Top Navigation Bar -->
        <div class="flex items-center justify-between h-16">
          <!-- Logo with Section Indicator -->
          <div class="flex items-center space-x-4">
            <router-link to="/" class="flex-shrink-0 flex items-center space-x-2">
              <img class="h-8 w-auto" src="/logo.svg" alt="Maison Truvra" />
              <div v-if="!isAdminLoginPage" class="hidden sm:block">
                <div class="text-xs font-medium text-gray-500 uppercase tracking-wide">{{ sectionTitle }}</div>
                <div class="text-sm font-semibold" :class="sectionTitleColor">{{ sectionSubtitle }}</div>
              </div>
            </router-link>
          </div>

          <!-- Enhanced Section Selector -->
          <div v-if="!isAdminLoginPage" class="hidden lg:flex items-center space-x-1 bg-white/80 backdrop-blur-sm rounded-xl p-1 shadow-lg border border-white/20">
            <button
              @click="switchSection('b2c')"
              :class="[
                'px-6 py-3 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105',
                currentSection === 'b2c' 
                  ? 'bg-gradient-to-r from-brand-burgundy to-brand-burgundy/90 text-white shadow-lg' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50'
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
                'px-6 py-3 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105',
                currentSection === 'b2b' 
                  ? 'bg-gradient-to-r from-brand-burgundy to-brand-burgundy/90 text-white shadow-lg' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50'
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
                'px-6 py-3 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105',
                currentSection === 'admin' 
                  ? 'bg-gradient-to-r from-brand-burgundy to-brand-burgundy/90 text-white shadow-lg' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50'
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

          <!-- Mobile Section Selector -->
          <div v-if="!isAdminLoginPage" class="lg:hidden">
            <button @click="showMobileMenu = !showMobileMenu" class="p-2 rounded-lg text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          <!-- Right side actions -->
          <div class="flex items-center space-x-2">
            <!-- Language Switcher -->
            <div class="relative">
              <button @click="toggleLanguage" class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-brand-cream/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-burgundy transition-colors">
                <span class="text-sm font-medium">{{ currentLanguage.toUpperCase() }}</span>
              </button>
            </div>

            <!-- Search Button -->
            <button @click="openSearch" class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-brand-cream/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-burgundy transition-colors">
              <span class="sr-only">Search</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>

            <!-- User Account -->
            <router-link to="/account" class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-brand-cream/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-burgundy transition-colors">
              <span class="sr-only">View account</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </router-link>

            <!-- Cart Icon -->
            <router-link to="/cart" class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-brand-cream/50 relative transition-colors">
              <span class="sr-only">View cart</span>
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              <span v-if="cartCount > 0" class="absolute -top-1 -right-1 block h-4 w-4 rounded-full bg-brand-burgundy text-white text-xs flex items-center justify-center animate-pulse">{{ cartCount }}</span>
            </router-link>
          </div>
        </div>

        <!-- Mobile Menu -->
        <div v-if="showMobileMenu && !isAdminLoginPage" class="lg:hidden border-t border-gray-200 bg-white/95 backdrop-blur-sm">
          <div class="px-2 pt-2 pb-3 space-y-1">
            <button
              @click="switchSection('b2c'); showMobileMenu = false"
              :class="[
                'w-full flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors',
                currentSection === 'b2c' 
                  ? 'bg-brand-burgundy text-white' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50'
              ]"
            >
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              Boutique
            </button>
            
            <button
              @click="switchSection('b2b'); showMobileMenu = false"
              :class="[
                'w-full flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors',
                currentSection === 'b2b' 
                  ? 'bg-brand-burgundy text-white' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50'
              ]"
            >
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              Professionnels
            </button>
            
            <button
              @click="switchSection('admin'); showMobileMenu = false"
              :class="[
                'w-full flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors',
                currentSection === 'admin' 
                  ? 'bg-brand-burgundy text-white' 
                  : 'text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50'
              ]"
            >
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Administration
            </button>
          </div>
        </div>

        <!-- Section-specific Navigation -->
        <div v-if="currentSection !== 'admin' && !isAdminLoginPage" class="border-t border-gray-200/50 bg-white/80 backdrop-blur-sm">
          <nav class="flex space-x-8 py-4">
            <router-link 
              v-for="item in sectionNavigation" 
              :key="item.name" 
              :to="item.href"
              class="text-gray-500 hover:text-brand-burgundy px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 hover:bg-brand-cream/30"
              active-class="text-brand-burgundy bg-brand-cream/50 font-semibold"
            >
              {{ item.name }}
            </router-link>
          </nav>
        </div>
        
        <!-- Breadcrumb Navigation -->
        <div v-if="showBreadcrumb && !isAdminLoginPage" class="border-t border-gray-200/50 bg-white/80 backdrop-blur-sm px-4 sm:px-6 lg:px-8 py-3">
          <UnifiedBreadcrumb />
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1">
      <!-- B2C Section -->
      <div v-if="currentSection === 'b2c'" class="min-h-screen bg-gradient-to-br from-brand-cream/30 to-white">
        <router-view />
      </div>

      <!-- B2B Section -->
      <div v-if="currentSection === 'b2b'" class="min-h-screen bg-gradient-to-br from-gray-50 to-brand-cream/20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <!-- Section Header -->
          <div class="mb-8">
            <div class="bg-gradient-to-r from-brand-burgundy to-brand-burgundy/90 rounded-2xl p-8 text-white shadow-xl">
              <div class="flex items-center space-x-4 mb-4">
                <div class="p-3 bg-white/20 rounded-xl">
                  <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <h1 class="text-3xl font-bold">Espace Professionnel</h1>
                  <p class="text-brand-cream/90 text-lg">Gérez vos commandes, demandes de devis et accédez à nos services B2B</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- B2B Content -->
          <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div class="p-8">
              <router-view />
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Login Page -->
      <div v-if="isAdminLoginPage" class="min-h-screen bg-gradient-to-br from-gray-900 to-brand-dark-brown">
        <router-view />
      </div>

      <!-- Admin Section -->
      <div v-if="currentSection === 'admin' && !isAdminLoginPage" class="flex h-screen bg-gradient-to-br from-gray-100 to-gray-200">
        <!-- Admin Sidebar -->
        <aside class="w-72 bg-gradient-to-b from-gray-800 to-gray-900 text-white flex-shrink-0 shadow-2xl">
          <div class="p-6 text-lg font-semibold border-b border-gray-700">
            <div class="flex items-center space-x-3">
              <div class="p-2 bg-brand-burgundy/20 rounded-lg">
                <svg class="w-6 h-6 text-brand-cream" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <div class="text-brand-cream text-sm font-medium">Administration</div>
                <div class="text-white text-lg font-bold">Maison Truvra</div>
              </div>
            </div>
          </div>
          <nav class="mt-6 px-4">
            <ul class="space-y-2">
              <li v-for="item in adminNavItems" :key="item.name">
                <router-link 
                  :to="item.path" 
                  class="flex items-center p-3 rounded-xl hover:bg-gray-700/50 transition-all duration-200 group"
                  active-class="bg-brand-burgundy/20 text-brand-cream border-l-4 border-brand-cream"
                >
                  <component :is="item.icon" class="h-5 w-5 mr-3 group-hover:scale-110 transition-transform" />
                  <span class="text-sm font-medium">{{ item.name }}</span>
                </router-link>
              </li>
            </ul>
          </nav>
        </aside>

        <!-- Admin Main Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <header class="bg-white/90 backdrop-blur-sm shadow-lg p-6 flex justify-between items-center border-b border-gray-200">
            <div>
              <h1 class="text-2xl font-bold text-brand-dark-brown">Tableau de bord</h1>
              <p class="text-gray-600 text-sm">Gérez votre boutique et vos clients</p>
            </div>
            <div class="flex items-center space-x-4">
              <router-link to="/admin/profile" class="text-gray-600 hover:text-brand-burgundy px-4 py-2 rounded-lg hover:bg-brand-cream/50 transition-colors">
                Profil
              </router-link>
              <button @click="logout" class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition-all duration-200 hover:shadow-lg">
                Déconnexion
              </button>
            </div>
          </header>
          <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gradient-to-br from-gray-50 to-white p-8">
            <router-view />
          </main>
        </div>
      </div>
    </main>

    <!-- Footer for B2C section only -->
    <Footer v-if="currentSection === 'b2c'" />

    <!-- Section Indicator -->
    <SectionIndicator :current-section="currentSection" />

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
import UnifiedBreadcrumb from '@/components/layout/UnifiedBreadcrumb.vue';
import SectionIndicator from '@/components/ui/SectionIndicator.vue';

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
const showMobileMenu = ref(false);

// Check if we're on admin login page
const isAdminLoginPage = computed(() => route.path === '/admin/login');

// Show breadcrumb for certain routes
const showBreadcrumb = computed(() => {
  const hideBreadcrumbRoutes = ['/', '/b2c', '/b2b', '/admin-landing', '/admin/login'];
  return !hideBreadcrumbRoutes.includes(route.path) && !route.path.startsWith('/admin/') || route.path === '/admin';
});

// Computed properties
const cartCount = computed(() => cartStore.itemCount);
const currentLanguage = computed(() => locale.value);

// Section-specific styling
const sectionBackgroundClass = computed(() => {
  switch (currentSection.value) {
    case 'b2c':
      return 'bg-gradient-to-br from-brand-cream/30 to-white';
    case 'b2b':
      return 'bg-gradient-to-br from-gray-50 to-brand-cream/20';
    case 'admin':
      return 'bg-gradient-to-br from-gray-100 to-gray-200';
    default:
      return 'bg-gray-50';
  }
});

const headerClass = computed(() => {
  switch (currentSection.value) {
    case 'b2c':
      return 'bg-white/95 backdrop-blur-sm shadow-lg border-b border-gray-200/50';
    case 'b2b':
      return 'bg-white/90 backdrop-blur-sm shadow-lg border-b border-gray-200/50';
    case 'admin':
      return 'bg-white/95 backdrop-blur-sm shadow-lg border-b border-gray-200/50';
    default:
      return 'bg-white shadow-sm';
  }
});

const sectionTitle = computed(() => {
  switch (currentSection.value) {
    case 'b2c':
      return 'Boutique';
    case 'b2b':
      return 'Professionnels';
    case 'admin':
      return 'Administration';
    default:
      return '';
  }
});

const sectionSubtitle = computed(() => {
  switch (currentSection.value) {
    case 'b2c':
      return 'Découvrez nos truffes d\'exception';
    case 'b2b':
      return 'Services professionnels';
    case 'admin':
      return 'Gestion de la boutique';
    default:
      return '';
  }
});

const sectionTitleColor = computed(() => {
  switch (currentSection.value) {
    case 'b2c':
      return 'text-brand-burgundy';
    case 'b2b':
      return 'text-brand-burgundy';
    case 'admin':
      return 'text-gray-700';
    default:
      return 'text-gray-700';
  }
});

// Navigation items for each section
const sectionNavigation = computed(() => {
  if (currentSection.value === 'b2c') {
    return [
      { name: 'Accueil', href: '/b2c' },
      { name: 'Boutique', href: '/shop' },
      { name: 'Journal', href: '/le-journal' },
      { name: 'À propos', href: '/notre-maison' },
      { name: 'Professionnels', href: '/b2b' },
    ];
  } else if (currentSection.value === 'b2b') {
    return [
      { name: 'Accueil', href: '/b2b' },
      { name: 'Dashboard', href: '/pro/dashboard' },
      { name: 'Demander un devis', href: '/pro/request-quote' },
      { name: 'Mes devis', href: '/pro/my-quotes' },
      { name: 'Mes commandes', href: '/pro/orders' },
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
  showMobileMenu.value = false; // Close mobile menu when switching sections
  
  // Navigate to appropriate default route for each section
  switch (section) {
    case 'b2c':
      router.push('/b2c');
      break;
    case 'b2b':
      router.push('/b2b');
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
  // Use route meta if available, otherwise fallback to path-based detection
  if (route.meta?.section) {
    currentSection.value = route.meta.section;
  } else {
    const path = route.path;
    if (path.startsWith('/admin')) {
      currentSection.value = 'admin';
    } else if (path.startsWith('/pro')) {
      currentSection.value = 'b2b';
    } else {
      currentSection.value = 'b2c';
    }
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