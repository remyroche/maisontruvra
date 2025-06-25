<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
    <div v-if="dashboardStore.isLoading">Loading...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Stat Cards -->
      <div v-for="(stat, key) in dashboardStore.stats" :key="key" class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">{{ formatStatKey(key) }}</h3>
        <p class="mt-1 text-3xl font-semibold">{{ stat }}</p>
      </div>
    </div>

    <h2 class="text-xl font-bold mt-8 mb-4">Recent Activity</h2>
     <div v-if="dashboardStore.isLoading">Loading activity...</div>
    <ul v-else class="space-y-3">
        <li v-for="item in dashboardStore.recentActivity" :key="item.id" class="bg-white p-3 rounded-lg shadow-sm">
            <p>{{ item.description }} - <span class="text-gray-500 text-sm">{{ new Date(item.timestamp).toLocaleString() }}</span></p>
        </li>
    </ul>
  </div>
</template>
<script setup>
import { onMounted } from 'vue';
import { useAdminDashboardStore } from '@/js/stores/adminDashboard';
const dashboardStore = useAdminDashboardStore();
onMounted(() => dashboardStore.fetchDashboardData());
const formatStatKey = (key) => key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
</script>
