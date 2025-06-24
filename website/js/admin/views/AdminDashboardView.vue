<!--
 * FILENAME: website/js/admin/views/AdminDashboardView.vue
 * DESCRIPTION: The main dashboard/homepage for the Admin Portal.
 *
 * This view serves as the landing page after an admin logs in. It demonstrates
 * accessing reactive state from the `useAdminAuthStore` to display a personalized
 * welcome message. It will be the future home for key metrics and summary stats.
-->
<template>
  <AdminLayout>
    <div class="p-8 bg-white rounded-lg shadow-md">
      <h1 class="text-3xl font-bold text-gray-800 mb-4">
        Welcome back, {{ adminFirstName }}!
      </h1>
      <p class="text-gray-600">
        This is your central dashboard. From here, you can manage users, products, orders, and site settings.
      </p>
      <div v-if="authStore.isLoading" class="mt-4">
        <p>Loading your details...</p>
      </div>
      <div v-if="authStore.error" class="mt-4 text-red-500">
        <p>Authentication Error: {{ authStore.error }}</p>
      </div>
      
      <!-- Future Dashboard Widgets can go here -->
      <div class="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="bg-blue-100 border border-blue-200 p-6 rounded-lg">
              <h2 class="text-xl font-semibold text-blue-800">Users</h2>
              <p class="mt-2 text-gray-700">Manage all registered users and their roles.</p>
              <router-link to="/admin/users" class="mt-4 inline-block bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600">
                Go to Users
              </router-link>
          </div>
          <div class="bg-green-100 border border-green-200 p-6 rounded-lg">
              <h2 class="text-xl font-semibold text-green-800">Products</h2>
              <p class="mt-2 text-gray-700">Add, edit, and manage product inventory.</p>
               <button disabled class="mt-4 inline-block bg-gray-400 text-white py-2 px-4 rounded cursor-not-allowed">
                Coming Soon
              </button>
          </div>
          <div class="bg-yellow-100 border border-yellow-200 p-6 rounded-lg">
              <h2 class="text-xl font-semibold text-yellow-800">Orders</h2>
              <p class="mt-2 text-gray-700">View and process customer orders.</p>
              <button disabled class="mt-4 inline-block bg-gray-400 text-white py-2 px-4 rounded cursor-not-allowed">
                Coming Soon
              </button>
          </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { computed } from 'vue';
import { useAdminAuthStore } from '../../stores/adminAuth';
import AdminLayout from '../components/AdminLayout.vue';

const authStore = useAdminAuthStore();

// Use a computed property for a safe fallback if the user object is not yet loaded.
const adminFirstName = computed(() => {
  return authStore.adminUser ? authStore.adminUser.first_name : 'Admin';
});
</script>
