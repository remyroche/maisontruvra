<!--
 * FILENAME: website/js/admin/AdminApp.vue
 * DESCRIPTION: The root Vue component for the entire Admin Portal SPA.
 * UPDATED: Added the NotificationProvider to make notifications globally available.
-->
<template>
  <div id="admin-portal">
    <router-view></router-view>
    <NotificationProvider />
  </div>
</template>

<script setup>
import NotificationProvider from './components/NotificationProvider.vue';
</script>
