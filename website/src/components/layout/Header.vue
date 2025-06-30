<template>
  <header class="bg-white shadow-sm sticky top-0 z-40">
    <nav class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <router-link to="/" class="flex-shrink-0">
            <img class="h-8 w-auto" src="/logo.svg" alt="Maison Truvra" />
          </router-link>
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <!-- Navigation Links from your script -->
              <router-link v-for="item in navigation" :key="item.name" :to="item.href"
                class="text-gray-500 hover:text-primary px-3 py-2 rounded-md text-sm font-medium"
                active-class="text-primary">{{ $t(item.name) }}</router-link>
            </div>
          </div>
        </div>
        <div class="hidden md:block">
          <div class="ml-4 flex items-center md:ml-6">
            
            <!-- Language Switcher from your script -->
            <div class="relative">
              <button @click="toggleLanguage" class="p-1 rounded-full text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
                <span class="text-sm font-medium">{{ currentLanguage.toUpperCase() }}</span>
              </button>
            </div>

            <!-- Search Button from your script -->
            <button @click="openSearch" class="p-1 rounded-full text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ml-4">
              <span class="sr-only">Search</span>
              <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>

            <!-- Profile/Account from your script -->
            <router-link to="/account" class="p-1 rounded-full text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ml-4">
              <span class="sr-only">View account</span>
              <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </router-link>

            <!-- Cart Icon now links directly to the /cart page -->
            <router-link to="/cart" class="ml-4 p-1 rounded-full text-gray-400 hover:text-gray-600 relative">
                <span class="sr-only">View cart</span>
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                <span v-if="cartCount > 0" class="absolute top-0 right-0 block h-4 w-4 rounded-full bg-primary text-white text-xs flex items-center justify-center">{{ cartCount }}</span>
            </router-link>

          </div>
        </div>
        <!-- Mobile menu button here -->
      </div>
    </nav>
  </header>
</template>

<script setup>
import { computed } from 'vue';
import { useCartStore } from '@/stores/cart';
import { useI18n } from 'vue-i18n'; // Standard way to get i18n instance in script setup

const { t, locale } = useI18n();

// Navigation data remains the same
const navigation = [
  { name: 'header.shop', href: '/shop' },
  { name: 'header.journal', href: '/journal' },
  { name: 'header.about', href: '/notre-maison' },
  { name: 'header.professionals', href: '/professionnels' },
];

const cartStore = useCartStore();
// cartCount computed property remains the same
const cartCount = computed(() => cartStore.itemCount);

const openSearch = () => {
  // Logic to open search overlay
  console.log('Open search');
};

// No longer need openMiniCart, as it's now a direct link.

const currentLanguage = computed(() => locale.value);

const toggleLanguage = () => {
    const newLocale = currentLanguage.value === 'fr' ? 'en' : 'fr';
    locale.value = newLocale;
};

</script>
