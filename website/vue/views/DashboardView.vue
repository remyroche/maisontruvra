<template>
  <div v-if="!dashboardStore.isLoading && dashboardStore.data" class="p-4 sm:p-6 lg:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Welcome Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Welcome back, {{ userStore.profile.first_name }}!</h1>
        <p class="text-gray-600 mt-1">Here's a summary of your account activity.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Column -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Recent Orders -->
          <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Recent Orders</h2>
            <div v-if="dashboardStore.data.recentOrders.length > 0" class="space-y-4">
                <div v-for="order in dashboardStore.data.recentOrders" :key="order.id" class="flex justify-between items-center p-3 border rounded-md">
                    <div>
                        <p class="font-medium">Order #{{ order.id.slice(0, 8) }}</p>
                        <p class="text-sm text-gray-500">Placed on {{ new Date(order.created_at).toLocaleDateString() }}</p>
                    </div>
                    <div class="text-right">
                        <p class="font-semibold">€{{ order.total_amount }}</p>
                        <span :class="['px-2 inline-flex text-xs leading-5 font-semibold rounded-full', getStatusClass(order.status)]">
                            {{ order.status }}
                        </span>
                    </div>
                </div>
            </div>
            <p v-else class="text-gray-500">You haven't placed any orders yet.</p>
          </div>
        </div>

        <!-- Sidebar Column -->
        <div class="space-y-8">
            <!-- Loyalty Status -->
            <div v-if="dashboardStore.data.loyaltyStatus" class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Loyalty Status</h2>
                <div class="text-center">
                    <p class="text-4xl font-bold text-primary">{{ dashboardStore.data.loyaltyStatus.points }}</p>
                    <p class="text-gray-500">Points</p>
                </div>
                <div class="mt-4 text-center">
                    <p class="font-medium">{{ dashboardStore.data.loyaltyStatus.tier.name }} Tier</p>
                    <p class="text-sm text-gray-600">{{ dashboardStore.data.loyaltyStatus.tier.benefits }}</p>
                </div>
                 <router-link to="/rewards" class="block w-full text-center mt-6 px-4 py-2 bg-primary text-white font-semibold rounded-md hover:bg-indigo-700">
                    View Rewards
                </router-link>
            </div>
             <!-- Quick Actions -->
            <div class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Quick Links</h2>
                <ul class="space-y-2">
                    <li><router-link to="/account/profile" class="text-primary hover:underline">Edit Profile</router-link></li>
                    <li><router-link to="/account/orders" class="text-primary hover:underline">View All Orders</router-link></li>
                    <li><router-link to="/referrals" class="text-primary hover:underline">Refer a Friend</router-link></li>
                </ul>
            </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-center p-12">
      <p>Loading your dashboard...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useDashboardStore } from '../../js/stores/dashboard';
import { useUserStore } from '../../js/stores/user';

const dashboardStore = useDashboardStore();
const userStore = useUserStore();

onMounted(() => {
    dashboardStore.fetchDashboardData();
});

const getStatusClass = (status) => {
    const classes = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'processing': 'bg-blue-100 text-blue-800',
        'shipped': 'bg-green-100 text-green-800',
        'completed': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
}
</script>
