<template>
  <header class="bg-gray-800 shadow-sm sticky top-0 z-50">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex-shrink-0">
          <a href="/professionnels.html" aria-label="Portail Professionnel">
            <img class="h-8 w-auto" src="/assets/logo-white.svg" alt="Maison Truv-ra Pro Logo" />
          </a>
        </div>

        <div class="flex items-center space-x-4">
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
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../../js/stores/auth';
import { useNotificationStore } from '../../../js/stores/notification';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const router = useRouter();

/**
 * Handles the B2B user logout process.
 */
const logout = async () => {
  try {
    await authStore.logoutB2B();
    notificationStore.showNotification('Vous avez été déconnecté.', 'success');
    // Redirect to the professional login page after logout
    window.location.href = '/professionnels.html';
  } catch (error) {
    console.error('B2B Logout failed:', error);
    notificationStore.showNotification(error.data?.message || 'La déconnexion a échoué.', 'error');
  }
};
</script>

<style scoped>
/* You can add component-specific styles here if needed */
</style>
