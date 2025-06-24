<!--
 * FILENAME: website/js/admin/components/AdminLayout.vue
 * DESCRIPTION: The main layout component for the Admin Portal.
 * UPDATED: Refactored to use the new modular layout components.
-->
<template>
  <div class="flex h-screen bg-gray-100 font-sans">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-800 text-white flex flex-col flex-shrink-0">
      <div class="h-16 flex items-center justify-center px-4 text-2xl font-bold border-b border-gray-700 flex-shrink-0">
        Maison Truvra
      </div>
      <SidebarNav />
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white shadow-md p-4 flex justify-between items-center flex-shrink-0">
        <h1 class="text-xl font-semibold text-gray-800">{{ $route.name }}</h1>
        <UserMenu />
      </header>
      <main class="flex-1 p-6 overflow-y-auto">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import SidebarNav from './layout/SidebarNav.vue';
import UserMenu from './layout/UserMenu.vue';
</script>
