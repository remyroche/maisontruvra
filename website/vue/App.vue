<template>
    <!-- 
      The main App component. It renders the Notification system globally
      and then hands off control to the Vue Router.
      Layouts (Header, Footer, etc.) are handled within the specific
      route components like ShopApp.vue or B2BPortal.vue.
    -->
    <Notification />
    <router-view></router-view>
</template>

<script setup>
// Using <script setup> is the modern and recommended approach in Vue 3.
// It's more concise and performant.
import Notification from './components/ui/Notification.vue';

// The component is automatically named 'App' based on the filename.
// The 'Notification' component is automatically registered for use in the template.
</script>
