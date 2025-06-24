<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <!-- B2B Header -->
    <B2BHeader />

    <!-- Main content area for B2B pages -->
    <main class="flex-grow container mx-auto p-4 sm:p-6 lg:p-8">
      <!-- The router for the B2B section will render the specific page component here -->
      <router-view />
    </main>

    <!-- Global Notification System -->
    <Notification />
    
    <!-- Cookie Consent Banner -->
    <CookieBanner />

    <!-- B2B Footer -->
    <B2BFooter />

    <!-- B2B Search -->
    <B2BSearchOverlay />

  </div>
</template>

<script setup>
import B2BHeader from './layout/B2BHeader.vue';
import B2BFooter from './layout/B2BFooter.vue';
import Notification from './ui/Notification.vue';
import CookieBanner from './layout/CookieBanner.vue';

// No page-specific components are imported here anymore.
// This component's sole responsibility is to provide the B2B layout shell.
</script>

<style scoped>
/* Scoped styles for the B2B portal layout can be added here if needed */
</style>
