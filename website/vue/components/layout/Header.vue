<template>
  <header class="bg-white shadow-sm sticky top-0 z-40">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex-shrink-0">
          <a href="/" aria-label="Page d'accueil">
            <img class="h-8 w-auto" src="/assets/logo.svg" alt="Maison Truv-ra Logo" />
          </a>
        </div>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex md:space-x-8">
          <a href="/products.html" class="text-base font-medium text-gray-500 hover:text-gray-900">Boutique</a>
          <a href="/notre-maison.html" class="text-base font-medium text-gray-500 hover:text-gray-900">Notre Maison</a>
          <a href="/le-journal.html" class="text-base font-medium text-gray-500 hover:text-gray-900">Le Journal</a>
          <a href="/professionnels.html" class="text-base font-medium text-gray-500 hover:text-gray-900">Espace Pro</a>
        </nav>

        <div class="flex items-center space-x-4">
           <a href="/account/profile.html" class="text-gray-500 hover:text-gray-700" aria-label="Mon compte">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </a>
          
          <!-- Mini Cart will be loaded here -->
          <div id="mini-cart-container"></div>
          
          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button @click="isMobileMenuOpen = !isMobileMenuOpen" type="button" class="bg-white p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500" aria-expanded="false">
              <span class="sr-only">Ouvrir le menu principal</span>
              <svg v-if="!isMobileMenuOpen" class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg v-else class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile menu, show/hide based on menu state. -->
    <div v-show="isMobileMenuOpen" class="md:hidden" id="mobile-menu">
      <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
        <a href="/products.html" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Boutique</a>
        <a href="/notre-maison.html" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Notre Maison</a>
        <a href="/le-journal.html" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Le Journal</a>
        <a href="/professionnels.html" class="text-gray-500 hover:text-gray-900 hover:bg-gray-50 block px-3 py-2 rounded-md text-base font-medium">Espace Pro</a>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// This script loads the MiniCart Vue component into the #mini-cart-container div.
// It's a way to integrate Vue components into specific parts of a non-SPA page.
import '../../../js/vue/mini-cart-loader.js';

const isMobileMenuOpen = ref(false);
</script>

