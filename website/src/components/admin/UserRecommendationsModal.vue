<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
    <div class="relative top-10 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/4 xl:w-2/3 shadow-lg rounded-md bg-white max-h-screen overflow-y-auto" @click.stop>
      <!-- Header -->
      <div class="flex items-center justify-between pb-4 border-b sticky top-0 bg-white z-10">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">User Recommendations</h3>
          <p v-if="userRecommendations" class="text-sm text-gray-600">
            {{ userRecommendations.user_name }} ({{ userRecommendations.user_email }})
          </p>
        </div>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-2 text-gray-600">Loading user recommendations...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="mt-4">
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex">
            <svg class="w-5 h-5 text-red-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <div>
              <p class="text-sm font-medium text-red-800">Failed to load recommendations</p>
              <p class="text-sm text-red-600 mt-1">{{ error }}</p>
            </div>
          </div>
        </div>
        <div class="mt-4 flex justify-center">
          <button
            @click="loadUserRecommendations"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md"
          >
            Retry
          </button>
        </div>
      </div>

      <!-- Content -->
      <div v-else-if="userRecommendations" class="mt-4">
        <!-- User Info Card -->
        <div class="bg-gray-50 rounded-lg p-4 mb-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h4 class="font-medium text-gray-900 mb-2">User Information</h4>
              <div class="space-y-1 text-sm">
                <p><span class="font-medium">ID:</span> {{ userRecommendations.user_id }}</p>
                <p><span class="font-medium">Name:</span> {{ userRecommendations.user_name || 'N/A' }}</p>
                <p><span class="font-medium">Email:</span> {{ userRecommendations.user_email }}</p>
              </div>
            </div>
            <div>
              <h4 class="font-medium text-gray-900 mb-2">Recommendations</h4>
              <div class="space-y-1 text-sm">
                <p><span class="font-medium">Total:</span> {{ userRecommendations.recommendation_count }}</p>
                <p><span class="font-medium">Type:</span> 
                  <span :class="recommendationType.color" class="px-2 py-1 text-xs font-medium rounded-full">
                    {{ recommendationType.label }}
                  </span>
                </p>
              </div>
            </div>
            <div>
              <h4 class="font-medium text-gray-900 mb-2">Actions</h4>
              <div class="space-y-2">
                <button
                  @click="refreshRecommendations"
                  :disabled="refreshing"
                  class="w-full px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
                >
                  {{ refreshing ? 'Refreshing...' : 'Refresh Recommendations' }}
                </button>
                <button
                  @click="exportUserData"
                  class="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md"
                >
                  Export Data
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommendations List -->
        <div v-if="userRecommendations.recommendations.length > 0">
          <div class="flex items-center justify-between mb-4">
            <h4 class="text-lg font-medium text-gray-900">Product Recommendations</h4>
            <div class="flex items-center space-x-2">
              <label class="text-sm text-gray-600">View:</label>
              <select
                v-model="viewMode"
                class="border border-gray-300 rounded-md px-2 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="grid">Grid View</option>
                <option value="list">List View</option>
              </select>
            </div>
          </div>

          <!-- Grid View -->
          <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="(product, index) in userRecommendations.recommendations"
              :key="product.id || index"
              class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <!-- Product Image Placeholder -->
              <div class="w-full h-32 bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              
              <!-- Product Info -->
              <div>
                <h5 class="font-medium text-gray-900 mb-1 line-clamp-2">
                  {{ product.name || `Product #${product.id}` }}
                </h5>
                <p v-if="product.description" class="text-sm text-gray-600 mb-2 line-clamp-2">
                  {{ product.description }}
                </p>
                <div class="flex items-center justify-between">
                  <span v-if="product.price" class="text-lg font-semibold text-gray-900">
                    €{{ formatPrice(product.price) }}
                  </span>
                  <span v-if="product.category" class="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full">
                    {{ product.category }}
                  </span>
                </div>
                <div class="mt-2 flex items-center justify-between text-xs text-gray-500">
                  <span>ID: {{ product.id }}</span>
                  <span v-if="product.stock_quantity !== undefined">
                    Stock: {{ product.stock_quantity }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- List View -->
          <div v-else class="space-y-3">
            <div
              v-for="(product, index) in userRecommendations.recommendations"
              :key="product.id || index"
              class="bg-white border border-gray-200 rounded-lg p-4 flex items-center space-x-4 hover:shadow-md transition-shadow"
            >
              <!-- Product Image Placeholder -->
              <div class="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              
              <!-- Product Info -->
              <div class="flex-1 min-w-0">
                <h5 class="font-medium text-gray-900 truncate">
                  {{ product.name || `Product #${product.id}` }}
                </h5>
                <p v-if="product.description" class="text-sm text-gray-600 truncate">
                  {{ product.description }}
                </p>
                <div class="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                  <span>ID: {{ product.id }}</span>
                  <span v-if="product.category">Category: {{ product.category }}</span>
                  <span v-if="product.stock_quantity !== undefined">Stock: {{ product.stock_quantity }}</span>
                </div>
              </div>
              
              <!-- Price -->
              <div v-if="product.price" class="text-right">
                <span class="text-lg font-semibold text-gray-900">€{{ formatPrice(product.price) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- No Recommendations -->
        <div v-else class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No recommendations available</h3>
          <p class="mt-1 text-sm text-gray-500">This user doesn't have any product recommendations yet.</p>
          <div class="mt-4">
            <button
              @click="refreshRecommendations"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md"
            >
              Generate Recommendations
            </button>
          </div>
        </div>

        <!-- Recommendation Algorithm Info -->
        <div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 class="font-medium text-blue-900 mb-2">How Recommendations Work</h4>
          <div class="text-sm text-blue-800 space-y-1">
            <p v-if="hasPersonalizedRecommendations">
              <strong>Personalized:</strong> Based on this user's purchase history and preferred categories.
            </p>
            <p v-else>
              <strong>General:</strong> Based on popular products since this user has no purchase history.
            </p>
            <p>Recommendations are updated automatically when users make new purchases.</p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end space-x-3 pt-4 border-t mt-6 sticky bottom-0 bg-white">
        <button
          @click="closeModal"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAdminRecommendationsStore } from '@/stores/adminRecommendations';

// Props
const props = defineProps({
  userId: {
    type: [Number, String],
    required: true
  }
});

// Emits
const emit = defineEmits(['close']);

// Store
const store = useAdminRecommendationsStore();

// Reactive data
const loading = ref(false);
const refreshing = ref(false);
const error = ref(null);
const userRecommendations = ref(null);
const viewMode = ref('grid');

// Computed
const recommendationType = computed(() => {
  if (!userRecommendations.value) return { label: 'Unknown', color: 'bg-gray-100 text-gray-800' };
  
  // Simple heuristic: if user has recommendations, check if they seem personalized
  // This could be enhanced with actual data from the backend
  const hasRecommendations = userRecommendations.value.recommendation_count > 0;
  
  if (hasRecommendations) {
    return { label: 'Personalized', color: 'bg-green-100 text-green-800' };
  } else {
    return { label: 'General', color: 'bg-yellow-100 text-yellow-800' };
  }
});

const hasPersonalizedRecommendations = computed(() => {
  return recommendationType.value.label === 'Personalized';
});

// Methods
const closeModal = () => {
  emit('close');
};

const loadUserRecommendations = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const data = await store.fetchUserRecommendations(props.userId, 20); // Get more recommendations for detail view
    userRecommendations.value = data;
  } catch (err) {
    error.value = err.message || 'Failed to load user recommendations';
    console.error('Error loading user recommendations:', err);
  } finally {
    loading.value = false;
  }
};

const refreshRecommendations = async () => {
  refreshing.value = true;
  
  try {
    // In a real implementation, this would trigger a refresh of recommendations
    // For now, we'll just reload the current data
    await loadUserRecommendations();
  } catch (err) {
    console.error('Error refreshing recommendations:', err);
  } finally {
    refreshing.value = false;
  }
};

const exportUserData = () => {
  if (!userRecommendations.value) return;
  
  const exportData = {
    user_info: {
      user_id: userRecommendations.value.user_id,
      user_email: userRecommendations.value.user_email,
      user_name: userRecommendations.value.user_name,
      recommendation_count: userRecommendations.value.recommendation_count
    },
    recommendations: userRecommendations.value.recommendations,
    export_date: new Date().toISOString(),
    recommendation_type: recommendationType.value.label
  };
  
  const jsonContent = JSON.stringify(exportData, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `user_${props.userId}_recommendations.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const formatPrice = (price) => {
  return typeof price === 'number' ? price.toFixed(2) : price;
};

// Lifecycle
onMounted(() => {
  loadUserRecommendations();
});
</script>

<style lang="postcss" scoped>
/* Line clamp utilities */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}

/* Modal animations */
.fixed {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.relative {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background-color: #f1f5f9; /* bg-gray-100 */
  border-radius: 0.25rem; /* rounded */
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #9ca3af; /* bg-gray-400 */
  border-radius: 0.25rem; /* rounded */
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background-color: #6b7280; /* bg-gray-500 */
}
</style>