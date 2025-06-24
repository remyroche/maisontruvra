<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <!-- B2C Header -->
    <Header />

    <!-- Main content area for B2C pages -->
    <main class="flex-grow">
      <router-view />
    </main>

    <!-- Global Notification System -->
    <Notification />
    
    <!-- Cookie Consent Banner -->
    <CookieBanner />

    <!-- B2C Footer -->
    <Footer />
  </div>
</template>

<script setup>
import Header from './components/layout/Header.vue';
import Footer from './components/layout/Footer.vue';
import Notification from './components/ui/Notification.vue';
import CookieBanner from './components/layout/CookieBanner.vue';

// The script block is minimal as the layout is primarily structural.
// Page-specific logic resides within the components loaded by the router.
</script>

<style>
/* Global styles can be placed here or in a separate CSS file imported in main.js */
</style>
