<template>
  <div class="manage-recommendations">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Customer Recommendations</h1>
        <p class="text-gray-600 mt-1">Manage and view product recommendations for all customers</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="exportRecommendations('csv')"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center"
          :disabled="loading"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export CSV
        </button>
        <button
          @click="refreshData"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center"
          :disabled="loading"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8" v-if="summary">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Active Users</p>
            <p class="text-2xl font-semibold text-gray-900">{{ summary.total_active_users }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Personalized</p>
            <p class="text-2xl font-semibold text-gray-900">{{ summary.users_with_personalized_recommendations }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">General</p>
            <p class="text-2xl font-semibold text-gray-900">{{ summary.users_with_general_recommendations }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Selected Users</p>
            <p class="text-2xl font-semibold text-gray-900">{{ selectedUserCount }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="bg-white rounded-lg shadow mb-6">
      <div class="p-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <!-- Search -->
          <div class="flex-1 max-w-md">
            <div class="relative">
              <input
                v-model="searchQuery"
                @input="handleSearch"
                type="text"
                placeholder="Search users by email, name, or ID..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Bulk Actions -->
          <div class="flex items-center space-x-3">
            <select
              v-model="recommendationsPerUser"
              @change="refreshData"
              class="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="3">3 per user</option>
              <option value="5">5 per user</option>
              <option value="8">8 per user</option>
              <option value="10">10 per user</option>
            </select>

            <button
              @click="selectAllUsers"
              class="text-blue-600 hover:text-blue-800 font-medium"
              :disabled="!hasRecommendations"
            >
              Select All
            </button>

            <button
              @click="clearSelection"
              class="text-gray-600 hover:text-gray-800 font-medium"
              :disabled="selectedUserCount === 0"
            >
              Clear
            </button>

            <button
              @click="showBulkModal = true"
              class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
              :disabled="!canPerformBulkOperations"
            >
              Bulk Actions ({{ selectedUserCount }})
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Results (when searching) -->
    <div v-if="searchQuery && searchResults.length > 0" class="bg-white rounded-lg shadow mb-6">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Search Results</h3>
        <div class="space-y-3">
          <div
            v-for="user in searchResults"
            :key="user.user_id"
            class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div class="flex items-center space-x-3">
              <input
                type="checkbox"
                :checked="isUserSelected(user.user_id)"
                @change="toggleUserSelection(user.user_id)"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <div>
                <p class="font-medium text-gray-900">{{ user.user_name || 'N/A' }}</p>
                <p class="text-sm text-gray-600">{{ user.user_email }}</p>
                <p class="text-xs text-gray-500">ID: {{ user.user_id }} | Registered: {{ formatDate(user.registration_date) }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span
                :class="user.has_recommendations ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                class="px-2 py-1 text-xs font-medium rounded-full"
              >
                {{ user.has_recommendations ? 'Has Recommendations' : 'No Recommendations' }}
              </span>
              <button
                @click="viewUserRecommendations(user.user_id)"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Recommendations Table -->
    <div class="bg-white rounded-lg shadow">
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Customer Recommendations</h3>
          <div class="text-sm text-gray-600">
            Showing {{ allRecommendations.length }} of {{ pagination.total_users }} users
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-2 text-gray-600">Loading recommendations...</span>
        </div>

        <!-- Recommendations Table -->
        <div v-else-if="hasRecommendations" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    :checked="selectedUserCount === allRecommendations.length && allRecommendations.length > 0"
                    @change="selectedUserCount === allRecommendations.length ? clearSelection() : selectAllUsers()"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  >
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recommendations</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Activity</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="userRec in allRecommendations"
                :key="userRec.user_id"
                :class="{ 'bg-blue-50': isUserSelected(userRec.user_id) }"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    :checked="isUserSelected(userRec.user_id)"
                    @change="toggleUserSelection(userRec.user_id)"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  >
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ userRec.user_name || 'N/A' }}</div>
                    <div class="text-sm text-gray-500">{{ userRec.user_email }}</div>
                    <div class="text-xs text-gray-400">ID: {{ userRec.user_id }}</div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div v-if="userRec.error" class="text-red-600 text-sm">
                    Error: {{ userRec.error }}
                  </div>
                  <div v-else-if="userRec.recommendations.length > 0">
                    <div class="flex items-center mb-2">
                      <span class="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
                        {{ userRec.recommendation_count }} recommendations
                      </span>
                    </div>
                    <div class="space-y-1">
                      <div
                        v-for="(rec, index) in userRec.recommendations.slice(0, 2)"
                        :key="index"
                        class="text-sm text-gray-600 truncate"
                      >
                        {{ rec.name || `Product #${rec.id}` }}
                      </div>
                      <div v-if="userRec.recommendations.length > 2" class="text-xs text-gray-500">
                        +{{ userRec.recommendations.length - 2 }} more...
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-gray-500 text-sm">No recommendations</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div>Registered: {{ formatDate(userRec.registration_date) }}</div>
                  <div v-if="userRec.last_login">Last login: {{ formatDate(userRec.last_login) }}</div>
                  <div v-else class="text-gray-400">Never logged in</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="viewUserRecommendations(userRec.user_id)"
                    class="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    View Details
                  </button>
                  <button
                    @click="refreshUserRecommendations(userRec.user_id)"
                    class="text-green-600 hover:text-green-900"
                  >
                    Refresh
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No recommendations found</h3>
          <p class="mt-1 text-sm text-gray-500">Get started by refreshing the data or checking your filters.</p>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.total_pages > 1" class="flex items-center justify-between mt-6">
          <div class="text-sm text-gray-700">
            Page {{ pagination.page }} of {{ pagination.total_pages }}
          </div>
          <div class="flex space-x-2">
            <button
              @click="prevPage"
              :disabled="!pagination.has_prev"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              @click="nextPage"
              :disabled="!pagination.has_next"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Operations Modal -->
    <BulkOperationsModal
      v-if="showBulkModal"
      :selected-users="selectedUsers"
      :user-data="allRecommendations"
      @close="showBulkModal = false"
      @bulk-operation="handleBulkOperation"
    />

    <!-- User Recommendations Detail Modal -->
    <UserRecommendationsModal
      v-if="showUserModal"
      :user-id="selectedUserId"
      @close="showUserModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAdminRecommendationsStore } from '@/stores/adminRecommendations';
import { useDateFormatter } from '@/composables/useDateFormatter';
import BulkOperationsModal from '@/components/admin/BulkOperationsModal.vue';
import UserRecommendationsModal from '@/components/admin/UserRecommendationsModal.vue';

// Store and composables
const store = useAdminRecommendationsStore();
const { formatDate } = useDateFormatter();

// Reactive data
const searchQuery = ref('');
const recommendationsPerUser = ref(5);
const showBulkModal = ref(false);
const showUserModal = ref(false);
const selectedUserId = ref(null);
const searchTimeout = ref(null);

// Computed properties
const {
  loading,
  summary,
  allRecommendations,
  pagination,
  selectedUsers,
  searchResults,
  searchLoading,
  hasRecommendations,
  selectedUserCount,
  canPerformBulkOperations
} = store;

// Methods
const refreshData = async () => {
  await Promise.all([
    store.fetchSummary(),
    store.fetchAllRecommendations({ limit_per_user: recommendationsPerUser.value })
  ]);
};

const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
  
  searchTimeout.value = setTimeout(() => {
    if (searchQuery.value.trim()) {
      store.searchUsers(searchQuery.value);
    }
  }, 300);
};

const viewUserRecommendations = (userId) => {
  selectedUserId.value = userId;
  showUserModal.value = true;
};

const refreshUserRecommendations = async (userId) => {
  try {
    await store.fetchUserRecommendations(userId);
    await refreshData(); // Refresh the main table
  } catch (error) {
    console.error('Failed to refresh user recommendations:', error);
  }
};

const handleBulkOperation = async (operation, options) => {
  try {
    if (operation === 'generate') {
      await store.bulkGenerateRecommendations(selectedUsers.value, options.limit_per_user);
      await refreshData(); // Refresh data after bulk operation
    }
  } catch (error) {
    console.error('Bulk operation failed:', error);
  }
};

const exportRecommendations = async (format) => {
  try {
    await store.exportRecommendations(format, {
      limit_per_user: recommendationsPerUser.value
    });
  } catch (error) {
    console.error('Export failed:', error);
  }
};

// Store method proxies
const { 
  toggleUserSelection, 
  selectAllUsers, 
  clearSelection, 
  isUserSelected,
  nextPage,
  prevPage
} = store;

// Lifecycle
onMounted(() => {
  refreshData();
});

// Watchers
watch(searchQuery, (newValue) => {
  if (!newValue.trim()) {
    store.searchResults = [];
  }
});
</script>
<style lang="postcss" scoped>
.manage-recommendations {
  @apply p-6 max-w-7xl mx-auto;
}

/* Custom scrollbar for table */
.overflow-x-auto::-webkit-scrollbar {
  height: 8px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  @apply bg-gray-400 rounded;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500;
}
</style>