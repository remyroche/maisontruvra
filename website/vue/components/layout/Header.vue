<template>
  <header class="bg-white shadow-sm sticky top-0 z-40">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex-shrink-0">
          <!-- The logo links to the static homepage -->
          <a href="/" aria-label="Page d'accueil">
            <img class="h-8 w-auto" src="/assets/logo.svg" alt="Maison Truv-ra Logo" />
          </a>
        </div>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex md:space-x-8">
          <!-- Internal SPA link to the shop -->
          <router-link to="/shop" class="text-base font-medium text-gray-500 hover:text-gray-900">Boutique</router-link>
          <!-- External links to static pages -->
          <a href="/notre-maison" class="text-base font-medium text-gray-500 hover:text-gray-900">Notre Maison</a>
          <a href="/le-journal" class="text-base font-medium text-gray-500 hover:text-gray-900">Le Journal</a>
          <a href="/professionnels" class="text-base font-medium text-gray-500 hover:text-gray-900">Espace Pro</a>
        </nav>

        <div class="flex items-center space-x-4">
           <!-- Internal SPA link to the user account -->
           <router-link to="/account" class="text-gray-500 hover:text-gray-700" aria-label="Mon compte">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </router-link>
      
        <div class="flex items-center space-x-4">
          <!-- Search Button -->
          <button @click="searchStore.openOverlay" type="button" class="p-2 text-gray-500 hover:text-gray-700">
              <span class="sr-only">Rechercher</span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>
          </button>
          <LanguageSwitcher />
          <router-link to="/account" class="text-gray-500 hover:text-gray-700" aria-label="Mon compte">
          <!-- ... user icon svg ... -->
          </router-link>
          <div id="mini-cart-container"></div>
          <!-- ... mobile menu button ... -->
      
          
          <div id="mini-cart-container"></div>
  
          <div class="md:hidden">
            <button @click="isMobileMenuOpen = !isMobileMenuOpen" type="button" class="bg-white p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500" aria-expanded="false">
              <span class="sr-only">Ouvrir le menu principal</span>
              <svg v-if="!isMobileMenuOpen" class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
              <svg v-else class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-show="isMobileMenuOpen" class="md:hidden" id="mobile-menu">
      <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
        <router-link to="/shop" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Boutique</router-link>
        <a href="/notre-maison" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Notre Maison</a>
        <a href="/le-journal" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Le Journal</a>
        <a href="/professionnels" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Espace Pro</a>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
import '../../../js/vue/mini-cart-loader.js';
import LanguageSwitcher from './LanguageSwitcher.vue'; // Import the new component
import { useI18n } from 'vue-i18n';

const isMobileMenuOpen = ref(false);
</script>
