<template>
  <div class="bg-white rounded-lg shadow p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Customer Recommendations</h3>
      <router-link
        to="/admin/recommendations"
        class="text-blue-600 hover:text-blue-800 text-sm font-medium"
      >
        View All →
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      <span class="ml-2 text-gray-600 text-sm">Loading...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <svg class="mx-auto h-8 w-8 text-red-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-red-600">Failed to load recommendation data</p>
      <button
        @click="loadSummary"
        class="mt-2 text-xs text-blue-600 hover:text-blue-800"
      >
        Retry
      </button>
    </div>

    <!-- Content -->
    <div v-else-if="summary" class="space-y-4">
      <!-- Stats Grid -->
      <div class="grid grid-cols-2 gap-4">
        <div class="text-center p-3 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ summary.total_active_users || 0 }}</div>
          <div class="text-xs text-blue-800">Active Users</div>
        </div>
        <div class="text-center p-3 bg-green-50 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ summary.users_with_personalized_recommendations || 0 }}</div>
          <div class="text-xs text-green-800">Personalized</div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="space-y-2">
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Recommendation Coverage</span>
          <span class="text-gray-900 font-medium">{{ coveragePercentage }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${coveragePercentage}%` }"
          ></div>
        </div>
      </div>

      <!-- Popular Categories -->
      <div v-if="summary.popular_categories && summary.popular_categories.length > 0">
        <h4 class="text-sm font-medium text-gray-900 mb-2">Popular Categories</h4>
        <div class="space-y-1">
          <div
            v-for="category in summary.popular_categories.slice(0, 3)"
            :key="category.category_id"
            class="flex justify-between text-sm"
          >
            <span class="text-gray-600 truncate">Category {{ category.category_id }}</span>
            <span class="text-gray-900 font-medium">{{ category.order_count }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="pt-3 border-t border-gray-200">
        <div class="flex space-x-2">
          <router-link
            to="/admin/recommendations"
            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium py-2 px-3 rounded text-center transition-colors"
          >
            Manage All
          </router-link>
          <button
            @click="refreshData"
            :disabled="loading"
            class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium py-2 px-3 rounded transition-colors disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <svg class="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-sm text-gray-500">No recommendation data available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAdminRecommendationsStore } from '@/stores/adminRecommendations';

// Store
const store = useAdminRecommendationsStore();

// Reactive data
const loading = ref(false);
const error = ref(null);

// Computed
const summary = computed(() => store.summary);

const coveragePercentage = computed(() => {
  if (!summary.value || !summary.value.total_active_users) return 0;
  
  const totalWithRecommendations = 
    (summary.value.users_with_personalized_recommendations || 0) + 
    (summary.value.users_with_general_recommendations || 0);
  
  return Math.round((totalWithRecommendations / summary.value.total_active_users) * 100);
});

// Methods
const loadSummary = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    await store.fetchSummary();
  } catch (err) {
    error.value = err.message || 'Failed to load recommendation summary';
    console.error('Error loading recommendation summary:', err);
  } finally {
    loading.value = false;
  }
};

const refreshData = () => {
  loadSummary();
};

// Lifecycle
onMounted(() => {
  loadSummary();
});
</script>

<style scoped>
/* Ensure consistent spacing and hover effects */
.transition-colors {
  transition: background-color 0.2s ease, color 0.2s ease;
}

.transition-all {
  transition: all 0.3s ease;
}

/* Truncate text for long category names */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>