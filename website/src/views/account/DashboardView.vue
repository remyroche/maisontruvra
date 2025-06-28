<template>
  <div v-if="dashboardStore.isLoading" class="text-center p-12">
    <p>{{ i18n.loading }}</p>
  </div>
  <div v-else-if="dashboardStore.data" class="space-y-8">
    <!-- Welcome Header -->
    <div class="px-4">
      <h1 class="text-3xl font-bold text-gray-900">{{ i18n.welcome.replace('{name}', userStore.profile.first_name) }}</h1>
      <p class="text-gray-600 mt-1">{{ i18n.welcomeSubtitle }}</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Main Column -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Recent Orders -->
        <div class="bg-white p-6 rounded-lg shadow">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">{{ i18n.recentOrdersTitle }}</h2>
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
          <p v-else class="text-gray-500">{{ i18n.noOrders }}</p>
        </div>
      </div>

      <!-- Sidebar Column -->
      <div class="space-y-8">
          <!-- Loyalty Status -->
          <div v-if="dashboardStore.data.loyaltyStatus" class="bg-white p-6 rounded-lg shadow">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">{{ i18n.loyaltyStatusTitle }}</h2>
              <div class="text-center">
                  <p class="text-4xl font-bold text-indigo-600">{{ dashboardStore.data.loyaltyStatus.points }}</p>
                  <p class="text-gray-500">{{ i18n.points }}</p>
              </div>
              <div class="mt-4 text-center">
                  <p class="font-medium">{{ dashboardStore.data.loyaltyStatus.tier.name }} {{ i18n.tier }}</p>
                  <p class="text-sm text-gray-600">{{ dashboardStore.data.loyaltyStatus.tier.benefits }}</p>
              </div>
               <router-link :to="{ name: 'Rewards' }" class="block w-full text-center mt-6 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700">
                  {{ i18n.viewRewards }}
              </router-link>
          </div>
           <!-- Quick Actions -->
          <div class="bg-white p-6 rounded-lg shadow">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">{{ i18n.quickLinksTitle }}</h2>
              <ul class="space-y-2">
                  <li><router-link to="/account/profile" class="text-indigo-600 hover:underline">{{ i18n.editProfile }}</router-link></li>
                  <li><router-link to="/account/orders" class="text-indigo-600 hover:underline">{{ i18n.viewAllOrders }}</router-link></li>
                  <li><router-link :to="{ name: 'Referrals' }" class="text-indigo-600 hover:underline">{{ i18n.referFriend }}</router-link></li>
              </ul>
          </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import { useUserStore } from '@/stores/user';
import i18nData from '@/locales/pages/account-dashboard.json';

const dashboardStore = useDashboardStore();
const userStore = useUserStore();
const currentLang = ref('fr');
const i18n = computed(() => i18nData[currentLang.value]);

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