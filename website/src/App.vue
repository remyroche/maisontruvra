<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <!-- Header -->
    <Header />

    <!-- Main content area -->
    <main class="flex-grow">
      <router-view />
    </main>

    <!-- Global Notification System -->
    <Notification />
    
    <!-- Cookie Consent Banner -->
    <CookieBanner />

    <!-- Footer -->
    <Footer />
    
    <!-- Search Overlay -->
    <SearchOverlay />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import Header from '@/components/layout/Header.vue';
import Footer from '@/components/layout/Footer.vue';
import Notification from '@/components/ui/Notification.vue';
import CookieBanner from '@/components/layout/CookieBanner.vue';
import SearchOverlay from '@/components/search/SearchOverlay.vue';

const userStore = useUserStore();

// Check authentication status on app load
onMounted(async () => {
  if (userStore.isLoggedIn === null) {
    await userStore.checkAuthStatus();
  }
});
</script>

<style>
/* Global styles are imported in main.js */
</style>