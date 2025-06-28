<template>
  <header class="bg-white shadow-sm border-b">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex-shrink-0">
          <router-link to="/" class="flex items-center">
            <img class="h-8 w-auto" src="/logo.svg" alt="Maison Truvra" />
            <span class="ml-2 text-xl font-bold text-brand-burgundy">Maison Truvra</span>
          </router-link>
        </div>

        <!-- Navigation -->
        <nav class="hidden md:flex space-x-8">
          <router-link 
            to="/shop" 
            class="text-gray-700 hover:text-brand-burgundy px-3 py-2 text-sm font-medium"
            active-class="text-brand-burgundy"
          >
            Boutique
          </router-link>
          <router-link 
            to="/le-journal" 
            class="text-gray-700 hover:text-brand-burgundy px-3 py-2 text-sm font-medium"
            active-class="text-brand-burgundy"
          >
            Le Journal
          </router-link>
          <router-link 
            to="/notre-maison" 
            class="text-gray-700 hover:text-brand-burgundy px-3 py-2 text-sm font-medium"
            active-class="text-brand-burgundy"
          >
            Notre Maison
          </router-link>
          <router-link 
            to="/professionnels" 
            class="text-gray-700 hover:text-brand-burgundy px-3 py-2 text-sm font-medium"
            active-class="text-brand-burgundy"
          >
            Professionnels
          </router-link>
        </nav>

        <!-- Right side actions -->
        <div class="flex items-center space-x-4">
          <!-- Search -->
          <button 
            @click="toggleSearch"
            class="text-gray-700 hover:text-brand-burgundy p-2"
            aria-label="Rechercher"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>

          <!-- Cart -->
          <router-link 
            to="/cart" 
            class="relative text-gray-700 hover:text-brand-burgundy p-2"
            aria-label="Panier"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 6M7 13l-1.5-6m0 0L4 5M7 13h10m0 0l1.5 6M17 13l1.5 6" />
            </svg>
            <span 
              v-if="cartStore.itemCount > 0" 
              class="absolute -top-1 -right-1 bg-brand-burgundy text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
            >
              {{ cartStore.itemCount }}
            </span>
          </router-link>

          <!-- User Account -->
          <div v-if="userStore.isLoggedIn" class="relative">
            <button 
              @click="toggleUserMenu"
              class="flex items-center text-gray-700 hover:text-brand-burgundy p-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </button>
            
            <!-- User Dropdown -->
            <div 
              v-if="showUserMenu" 
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50"
              @click.away="showUserMenu = false"
            >
              <router-link 
                to="/account" 
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="showUserMenu = false"
              >
                Mon compte
              </router-link>
              <router-link 
                to="/account/orders" 
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="showUserMenu = false"
              >
                Mes commandes
              </router-link>
              <button 
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Se déconnecter
              </button>
            </div>
          </div>

          <!-- Login/Register -->
          <div v-else class="flex items-center space-x-2">
            <button 
              @click="showLoginModal = true"
              class="text-gray-700 hover:text-brand-burgundy text-sm font-medium"
            >
              Connexion
            </button>
          </div>

          <!-- Mobile menu button -->
          <button 
            @click="toggleMobileMenu"
            class="md:hidden text-gray-700 hover:text-brand-burgundy p-2"
            aria-label="Menu"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="showMobileMenu" class="md:hidden border-t border-gray-200 py-4">
        <div class="space-y-2">
          <router-link 
            to="/shop" 
            class="block text-gray-700 hover:text-brand-burgundy px-3 py-2 text-base font-medium"
            @click="showMobileMenu = false"
          >
            Boutique
          </router-link>
          <router-link 
            to="/le-journal" 
            class="block text-gray-700 hover:text-brand-burgundy px-3 py-2 text-base font-medium"
            @click="showMobileMenu = false"
          >
            Le Journal
          </router-link>
          <router-link 
            to="/notre-maison" 
            class="block text-gray-700 hover:text-brand-burgundy px-3 py-2 text-base font-medium"
            @click="showMobileMenu = false"
          >
            Notre Maison
          </router-link>
          <router-link 
            to="/professionnels" 
            class="block text-gray-700 hover:text-brand-burgundy px-3 py-2 text-base font-medium"
            @click="showMobileMenu = false"
          >
            Professionnels
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useCartStore } from '@/stores/cart';

const userStore = useUserStore();
const cartStore = useCartStore();

const showUserMenu = ref(false);
const showMobileMenu = ref(false);
const showLoginModal = ref(false);

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value;
}

function toggleMobileMenu() {
  showMobileMenu.value = !showMobileMenu.value;
}

function toggleSearch() {
  // This will be handled by the SearchOverlay component
  // You can emit an event or use a global store
}

async function handleLogout() {
  await userStore.logout();
  showUserMenu.value = false;
}
</script>