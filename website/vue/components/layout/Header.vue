<template>
  <header class="bg-cream shadow-md fixed top-0 left-0 right-0 z-50 transition-all duration-300">
    <div class="container mx-auto px-6 py-4 flex justify-between items-center">
      <!-- Logo -->
      <router-link :to="{ name: 'home' }" class="text-2xl font-serif text-dark-brown">
        Maison Trüvra
      </router-link>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-8">
        <router-link :to="{ name: 'catalogue' }" class="hover:text-truffle-burgundy transition-colors">Nos Produits</router-link>
        <a href="#" class="hover:text-truffle-burgundy transition-colors">Notre Histoire</a>
        <a href="#" class="hover:text-truffle-burgundy transition-colors">Contact</a>
      </nav>

      <!-- Icons & Mobile Menu Button -->
      <div class="flex items-center space-x-6">
        <router-link :to="{ name: 'cart' }" class="relative hover:text-truffle-burgundy transition-colors">
          <!-- Shopping Bag Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <span class="absolute -top-2 -right-2 bg-truffle-burgundy text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">0</span>
        </router-link>
        <router-link :to="{ name: 'profile' }" class="hover:text-truffle-burgundy transition-colors">
          <!-- User Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </router-link>
        <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="md:hidden">
          <!-- Hamburger Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
          </svg>
        </button>
      </div>
    </div>
    <!-- Mobile Menu -->
    <div v-show="isMobileMenuOpen" class="md:hidden bg-cream shadow-lg">
      <nav class="flex flex-col items-center space-y-4 py-4">
        <router-link :to="{ name: 'catalogue' }" @click="isMobileMenuOpen = false" class="hover:text-truffle-burgundy transition-colors">Nos Produits</router-link>
        <a href="#" @click="isMobileMenuOpen = false" class="hover:text-truffle-burgundy transition-colors">Notre Histoire</a>
        <a href="#" @click="isMobileMenuOpen = false" class="hover:text-truffle-burgundy transition-colors">Contact</a>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
const isMobileMenuOpen = ref(false);
</script>