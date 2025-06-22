<template>
  <div class="shop-layout">
    <Header />
    <!-- 
      The <main> element wraps the router-view.
      Padding-top is added to prevent content from being hidden
      underneath the fixed-position header.
    -->
    <main class="min-h-screen">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Header from '@/vue/components/layout/Header.vue';
import Footer from '@/vue/components/layout/Footer.vue';
</script>