<template>
  <header id="header" class="bg-white sticky top-0 z-50 shadow-md">
    <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
      <div class="flex items-center">
        <router-link :to="{ name: 'home' }">
          <img src="/img/logo.svg" alt="Maison Trüvra Logo" class="h-8">
        </router-link>
      </div>
      <div class="hidden lg:flex items-center space-x-6">
        <a href="/notre-maison.html" class="text-gray-700 hover:text-black transition-colors duration-300">Notre Maison</a>
        <router-link :to="{ name: 'catalogue' }" class="text-gray-700 hover:text-black transition-colors duration-300">Nos Produits</router-link>
        <a href="/le-journal.html" class="text-gray-700 hover:text-black transition-colors duration-300">Le Journal</a>
        <span class="text-gray-300">|</span>
        <router-link :to="{ name: 'pro-login' }" class="text-sm text-gray-600 hover:text-black transition-colors duration-300">Espace Professionnels</router-link>
      </div>
      <div class="flex items-center space-x-4">
        <button id="search-button" aria-label="Search">
          <svg class="h-6 w-6 text-gray-700 hover:text-black transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </button>
        <router-link :to="{ name: 'profile' }" aria-label="Mon Compte">
          <svg class="h-6 w-6 text-gray-700 hover:text-black transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
        </router-link>
        <router-link :to="{ name: 'cart' }" class="relative" aria-label="Shopping Cart">
          <svg class="h-6 w-6 text-gray-700 hover:text-black transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
          <span id="cart-item-count" class="absolute -top-2 -right-2 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">0</span>
        </router-link>
        <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="lg:hidden" aria-label="Open navigation menu">
          <svg class="h-6 w-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
        </button>
      </div>
    </nav>
    <div v-show="isMobileMenuOpen" class="lg:hidden">
      <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <a href="/notre-maison.html" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-black hover:bg-gray-50 transition-colors duration-300">Notre Maison</a>
          <router-link :to="{ name: 'catalogue' }" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-black hover:bg-gray-50 transition-colors duration-300">Nos Produits</router-link>
          <a href="/le-journal.html" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-black hover:bg-gray-50 transition-colors duration-300">Le Journal</a>
          <router-link :to="{ name: 'pro-login' }" class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-black hover:bg-gray-50 transition-colors duration-300">Espace Professionnels</router-link>
      </div>
      <button @click="isMobileMenuOpen = false" class="absolute top-4 right-4" aria-label="Close navigation menu">
           <svg class="h-6 w-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';

const isMobileMenuOpen = ref(false);
</script>
