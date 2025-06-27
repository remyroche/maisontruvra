<template>
  <header class="bg-gray-800 shadow-sm sticky top-0 z-50">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex-shrink-0">
          <router-link to="/pro/dashboard" aria-label="Portail Professionnel">
            <img class="h-8 w-auto" src="/assets/logo-white.svg" alt="Maison Truv-ra Pro Logo" />
          </router-link>
        </div>

        <div class="flex items-center space-x-4">
           <!-- B2B Search Button -->
          <button @click="b2bSearchStore.openOverlay" type="button" class="p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700">
            <span class="sr-only">Rechercher</span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>
          </button>

          <span v-if="authStore.isB2BAuthenticated && authStore.user" class="hidden sm:inline text-sm font-medium text-white">
            Bonjour, {{ authStore.user.first_name }}
          </span>
          <button
            @click="logout"
            class="p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
            aria-label="Se déconnecter"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
           <LanguageSwitcher />
           <button @click="logout" class="p-2 hover:text-primary">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>

          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '../../../js/stores/auth';
import { useNotificationStore } from '../../../js/stores/notification';
import { useB2BSearchStore } from '../../../js/stores/b2bSearch';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const logout = async () => {
  try {
    await authStore.logoutB2B();
    notificationStore.showNotification('Vous avez été déconnecté.', 'success');
    window.location.href = '/professionnels';
  } catch (error) {
    console.error('B2B Logout failed:', error);
    notificationStore.showNotification(error.data?.message || 'La déconnexion a échoué.', 'error');
  }
};
import B2BSearchOverlay from '../search/B2BSearchOverlay.vue';
import MiniCart from '../MiniCart.vue';
import LanguageSwitcher from './LanguageSwitcher.vue'; // Import the new component
import { useI18n } from 'vue-i18n';
import { useB2BPortalStore } from '../../../js/stores/b2b-portal';

const { t } = useI18n();
const b2bPortalStore = useB2BPortalStore();

</script>

</script>


