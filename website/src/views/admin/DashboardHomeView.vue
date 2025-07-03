<template>
  <div class="dashboard-home">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
      <p class="text-gray-600 mt-1">Welcome back! Here's what's happening with your store.</p>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <!-- Quick Stats Cards -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Users</p>
            <p class="text-2xl font-semibold text-gray-900">{{ totalUsers }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Orders</p>
            <p class="text-2xl font-semibold text-gray-900">{{ totalOrders }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Products</p>
            <p class="text-2xl font-semibold text-gray-900">{{ totalProducts }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Revenue</p>
            <p class="text-2xl font-semibold text-gray-900">€{{ totalRevenue }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Widgets Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mt-8">
      <!-- Recommendations Widget -->
      <RecommendationsDashboardWidget />

      <!-- Recent Orders Widget -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Recent Orders</h3>
          <router-link
            to="/admin/orders"
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View All →
          </router-link>
        </div>
        <div class="space-y-3">
          <div v-for="order in recentOrders" :key="order.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900">#{{ order.id }}</p>
              <p class="text-sm text-gray-600">{{ order.customer_name }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-900">€{{ order.total }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(order.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- System Status Widget -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Database</span>
            <span class="flex items-center text-green-600">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              Online
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">API Services</span>
            <span class="flex items-center text-green-600">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              Online
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Recommendations</span>
            <span class="flex items-center text-green-600">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              Active
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Cache</span>
            <span class="flex items-center text-green-600">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              Optimal
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="mt-8">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <router-link
          to="/admin/products"
          class="flex flex-col items-center p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <svg class="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <span class="text-sm font-medium text-gray-900">Add Product</span>
        </router-link>

        <router-link
          to="/admin/users"
          class="flex flex-col items-center p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <svg class="w-8 h-8 text-green-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
          </svg>
          <span class="text-sm font-medium text-gray-900">Manage Users</span>
        </router-link>

        <router-link
          to="/admin/orders"
          class="flex flex-col items-center p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <svg class="w-8 h-8 text-yellow-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <span class="text-sm font-medium text-gray-900">View Orders</span>
        </router-link>

        <router-link
          to="/admin/recommendations"
          class="flex flex-col items-center p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <svg class="w-8 h-8 text-purple-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span class="text-sm font-medium text-gray-900">Recommendations</span>
        </router-link>

        <router-link
          to="/admin/blog"
          class="flex flex-col items-center p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <svg class="w-8 h-8 text-indigo-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          <span class="text-sm font-medium text-gray-900">Manage Blog</span>
        </router-link>

        <router-link
          to="/admin/site-settings"
          class="flex flex-col items-center p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <svg class="w-8 h-8 text-gray-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span class="text-sm font-medium text-gray-900">Settings</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useDateFormatter } from '@/composables/useDateFormatter';
import RecommendationsDashboardWidget from '@/components/admin/RecommendationsDashboardWidget.vue';

// Composables
const { formatDate } = useDateFormatter();

// Reactive data
const totalUsers = ref(0);
const totalOrders = ref(0);
const totalProducts = ref(0);
const totalRevenue = ref(0);
const recentOrders = ref([]);

// Mock data - in a real app, this would come from API calls
const loadDashboardData = async () => {
  // Simulate API calls
  totalUsers.value = 1247;
  totalOrders.value = 3891;
  totalProducts.value = 156;
  totalRevenue.value = 45678.90;
  
  recentOrders.value = [
    {
      id: 'ORD-2024-001',
      customer_name: 'Marie Dubois',
      total: 89.50,
      created_at: new Date().toISOString()
    },
    {
      id: 'ORD-2024-002',
      customer_name: 'Jean Martin',
      total: 156.75,
      created_at: new Date(Date.now() - 86400000).toISOString() // Yesterday
    },
    {
      id: 'ORD-2024-003',
      customer_name: 'Sophie Laurent',
      total: 234.20,
      created_at: new Date(Date.now() - 172800000).toISOString() // 2 days ago
    }
  ];
};

// Lifecycle
onMounted(() => {
  loadDashboardData();
});
</script>

<style lang="postcss" scoped>
.dashboard-home {
  @apply p-6 max-w-7xl mx-auto;
}

.transition-shadow {
  transition: box-shadow 0.2s ease;
}
</style>