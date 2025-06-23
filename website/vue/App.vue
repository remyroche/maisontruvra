<template>
  <div>
    <Header />
    <Notification />
    <router-view></router-view>
    <Footer />
  </div>
</template>

<script setup>
import Notification from './components/ui/Notification.vue';
import Header from './components/layout/Header.vue';
import Footer from './components/layout/Footer.vue';
</script>

