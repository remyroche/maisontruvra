<!--
 * FILENAME: website/js/admin/AdminApp.vue
 * DESCRIPTION: The root Vue component for the entire Admin Portal SPA.
 *
 * This component is the entry point for the admin application. It simply
 * renders the main router view, which in turn will render the AdminLayout
 * and the appropriate page component based on the current URL.
-->
<template>
  <div id="admin-portal">
    <router-view></router-view>
  </div>
</template>

<script setup>
// This is the root component.
// Global setup, if any, could be performed here.
</script>
