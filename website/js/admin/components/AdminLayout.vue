<!--
 * FILENAME: website/js/admin/components/AdminLayout.vue
 * DESCRIPTION: The main layout component for the Admin Portal.
 *
 * UPDATED: Added navigation links for all remaining admin panel features.
-->
<template>
  <div class="flex h-screen bg-gray-100 font-sans">
    <aside class="w-64 bg-gray-800 text-white flex-shrink-0 overflow-y-auto">
      <div class="p-4 text-2xl font-bold border-b border-gray-700 sticky top-0 bg-gray-800">Maison Truvra</div>
      <nav class="mt-6 text-sm">
        <router-link to="/admin" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Dashboard</router-link>
        
        <h3 class="px-4 pt-4 pb-2 text-xs text-gray-500 font-bold uppercase tracking-wider">Content</h3>
        <router-link to="/admin/blog" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Blog</router-link>
        <router-link to="/admin/assets" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Assets</router-link>

        <h3 class="px-4 pt-4 pb-2 text-xs text-gray-500 font-bold uppercase tracking-wider">E-commerce</h3>
        <router-link to="/admin/orders" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Orders</router-link>
        <router-link to="/admin/products" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Products</router-link>
        <router-link to="/admin/categories" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Categories</router-link>
        <router-link to="/admin/collections" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Collections</router-link>
        <router-link to="/admin/reviews" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Reviews</router-link>
        
        <h3 class="px-4 pt-4 pb-2 text-xs text-gray-500 font-bold uppercase tracking-wider">Customers</h3>
        <router-link to="/admin/users" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Users</router-link>
        <router-link to="/admin/b2b" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">B2B Accounts</router-link>
        <router-link to="/admin/loyalty" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Loyalty</router-link>

        <h3 class="px-4 pt-4 pb-2 text-xs text-gray-500 font-bold uppercase tracking-wider">System</h3>
        <router-link to="/admin/settings" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Site Settings</router-link>
        <router-link to="/admin/audit-log" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">Audit Log</router-link>
        <router-link to="/admin/profile" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700" active-class="bg-gray-900">My Profile</router-link>

      </nav>
    </aside>
    <main class="flex-1 flex flex-col overflow-hidden">
        <header class="bg-white shadow-md p-4 flex justify-between items-center">
            <h1 class="text-xl font-semibold text-gray-800">{{ $route.name }}</h1>
            <div>
                <button @click="logout" class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded">Logout</button>
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
