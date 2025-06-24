<!--
 * FILENAME: website/js/admin/components/AdminLayout.vue
 * DESCRIPTION: The main layout component for the Admin Portal.
 *
 * UPDATED: Added a navigation link to the 'Manage Products' page in the sidebar.
-->
<template>
  <div class="flex h-screen bg-gray-100 font-sans">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-800 text-white flex-shrink-0">
      <div class="p-4 text-2xl font-bold border-b border-gray-700">Maison Truvra</div>
      <nav class="mt-6">
        <router-link
          to="/admin"
          class="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-700 hover:text-white"
          active-class="bg-gray-900 text-white"
        >
          <svg class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1V10a1 1 0 00-1-1H7a1 1 0 00-1 1v10a1 1 0 001 1h2z"></path></svg>
          Dashboard
        </router-link>
        <router-link
          to="/admin/users"
          class="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-700 hover:text-white"
          active-class="bg-gray-900 text-white"
        >
          <svg class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M15 21a6 6 0 00-9-5.197M15 11a4 4 0 110-8 4 4 0 010 8z" /></svg>
          Manage Users
        </router-link>
        <!-- --- New Nav Link --- -->
        <router-link
          to="/admin/products"
          class="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-700 hover:text-white"
          active-class="bg-gray-900 text-white"
        >
          <svg class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
          Manage Products
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white shadow-md p-4 flex justify-between items-center">
        <h1 class="text-xl font-semibold text-gray-800">{{ $route.name }}</h1>
        <div>
          <button @click="logout" class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded">
            Logout
          </button>
        </div>
      </header>
      <div class="flex-1 p-6 overflow-y-auto">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAdminAuthStore } from '../../stores/adminAuth';

const router = useRouter();
const authStore = useAdminAuthStore();

async function logout() {
  await authStore.logout();
  window.location.href = '/admin/login';
}
</script>

<style scoped>
.router-link-exact-active {
  background-color: #1a202c;
  color: white;
}
</style>
