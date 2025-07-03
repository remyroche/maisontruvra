<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white" @click.stop>
      <!-- Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Bulk Operations</h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="mt-4">
        <!-- Selected Users Summary -->
        <div class="bg-blue-50 rounded-lg p-4 mb-6">
          <h4 class="font-medium text-blue-900 mb-2">Selected Users ({{ selectedUsers.length }})</h4>
          <div class="max-h-32 overflow-y-auto">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
              <div
                v-for="userId in selectedUsers.slice(0, 10)"
                :key="userId"
                class="text-sm text-blue-800"
              >
                {{ getUserDisplayName(userId) }}
              </div>
            </div>
            <div v-if="selectedUsers.length > 10" class="text-sm text-blue-600 mt-2">
              +{{ selectedUsers.length - 10 }} more users...
            </div>
          </div>
        </div>

        <!-- Operation Selection -->
        <div class="space-y-6">
          <!-- Generate Recommendations -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center mb-3">
              <input
                id="generate-recommendations"
                v-model="selectedOperation"
                type="radio"
                value="generate"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              >
              <label for="generate-recommendations" class="ml-2 text-sm font-medium text-gray-900">
                Generate Fresh Recommendations
              </label>
            </div>
            <p class="text-sm text-gray-600 mb-3">
              Generate new product recommendations for all selected users. This will refresh their recommendation data.
            </p>
            <div v-if="selectedOperation === 'generate'" class="ml-6 space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Recommendations per user
                </label>
                <select
                  v-model="generateOptions.limit_per_user"
                  class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="3">3 recommendations</option>
                  <option value="5">5 recommendations</option>
                  <option value="8">8 recommendations</option>
                  <option value="10">10 recommendations</option>
                </select>
              </div>
              <div class="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <div class="flex">
                  <svg class="w-5 h-5 text-yellow-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                  <div>
                    <p class="text-sm text-yellow-800">
                      <strong>Note:</strong> This operation may take several minutes for large user sets. 
                      You'll receive a notification when it's complete.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Export Data -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center mb-3">
              <input
                id="export-data"
                v-model="selectedOperation"
                type="radio"
                value="export"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              >
              <label for="export-data" class="ml-2 text-sm font-medium text-gray-900">
                Export Selected Users' Data
              </label>
            </div>
            <p class="text-sm text-gray-600 mb-3">
              Export recommendation data for selected users to CSV format for analysis or marketing campaigns.
            </p>
            <div v-if="selectedOperation === 'export'" class="ml-6 space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Export format
                </label>
                <select
                  v-model="exportOptions.format"
                  class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="csv">CSV (Comma Separated Values)</option>
                  <option value="json">JSON (JavaScript Object Notation)</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Recommendations per user in export
                </label>
                <select
                  v-model="exportOptions.limit_per_user"
                  class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="5">5 recommendations</option>
                  <option value="10">10 recommendations</option>
                  <option value="15">15 recommendations</option>
                  <option value="20">20 recommendations</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Email Campaign Preparation -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center mb-3">
              <input
                id="email-campaign"
                v-model="selectedOperation"
                type="radio"
                value="email"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              >
              <label for="email-campaign" class="ml-2 text-sm font-medium text-gray-900">
                Prepare Email Campaign Data
              </label>
            </div>
            <p class="text-sm text-gray-600 mb-3">
              Generate recommendation data optimized for email marketing campaigns with personalized product suggestions.
            </p>
            <div v-if="selectedOperation === 'email'" class="ml-6 space-y-3">
              <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
                <div class="flex">
                  <svg class="w-5 h-5 text-blue-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <div>
                    <p class="text-sm text-blue-800">
                      <strong>Coming Soon:</strong> Email campaign integration will be available in the next update. 
                      For now, use the export function to get data for your email platform.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Progress Indicator -->
        <div v-if="isProcessing" class="mt-6 bg-gray-50 rounded-lg p-4">
          <div class="flex items-center">
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
            <div>
              <p class="text-sm font-medium text-gray-900">Processing bulk operation...</p>
              <p class="text-xs text-gray-600">This may take a few moments depending on the number of users selected.</p>
            </div>
          </div>
        </div>

        <!-- Operation Results -->
        <div v-if="operationResult" class="mt-6">
          <div
            :class="{
              'bg-green-50 border-green-200': operationResult.success,
              'bg-red-50 border-red-200': !operationResult.success,
              'bg-yellow-50 border-yellow-200': operationResult.partial
            }"
            class="border rounded-lg p-4"
          >
            <div class="flex">
              <svg
                v-if="operationResult.success"
                class="w-5 h-5 text-green-400 mr-2 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <svg
                v-else-if="operationResult.partial"
                class="w-5 h-5 text-yellow-400 mr-2 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              <svg
                v-else
                class="w-5 h-5 text-red-400 mr-2 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <div>
                <p
                  :class="{
                    'text-green-800': operationResult.success,
                    'text-red-800': !operationResult.success && !operationResult.partial,
                    'text-yellow-800': operationResult.partial
                  }"
                  class="text-sm font-medium"
                >
                  {{ operationResult.message }}
                </p>
                <div v-if="operationResult.details" class="mt-2 text-sm text-gray-600">
                  <ul class="list-disc list-inside space-y-1">
                    <li v-for="detail in operationResult.details" :key="detail">{{ detail }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end space-x-3 pt-4 border-t mt-6">
        <button
          @click="closeModal"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          :disabled="isProcessing"
        >
          Cancel
        </button>
        <button
          @click="executeOperation"
          :disabled="!selectedOperation || isProcessing"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isProcessing ? 'Processing...' : 'Execute Operation' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAdminRecommendationsStore } from '@/stores/adminRecommendations';

// Props
const props = defineProps({
  selectedUsers: {
    type: Array,
    required: true
  },
  userData: {
    type: Array,
    required: true
  }
});

// Emits
const emit = defineEmits(['close', 'bulk-operation']);

// Store
const store = useAdminRecommendationsStore();

// Reactive data
const selectedOperation = ref('');
const isProcessing = ref(false);
const operationResult = ref(null);

const generateOptions = ref({
  limit_per_user: 5
});

const exportOptions = ref({
  format: 'csv',
  limit_per_user: 5
});

// Computed
const getUserDisplayName = (userId) => {
  const user = props.userData.find(u => u.user_id === userId);
  return user ? `${user.user_name || 'N/A'} (${user.user_email})` : `User #${userId}`;
};

// Methods
const closeModal = () => {
  if (!isProcessing.value) {
    emit('close');
  }
};

const executeOperation = async () => {
  if (!selectedOperation.value || isProcessing.value) return;

  isProcessing.value = true;
  operationResult.value = null;

  try {
    switch (selectedOperation.value) {
      case 'generate':
        await executeGenerateOperation();
        break;
      case 'export':
        await executeExportOperation();
        break;
      case 'email':
        // Email campaign preparation - placeholder for future implementation
        operationResult.value = {
          success: false,
          message: 'Email campaign feature is not yet implemented.',
          details: ['This feature will be available in a future update.']
        };
        break;
      default:
        throw new Error('Unknown operation selected');
    }
  } catch (error) {
    console.error('Bulk operation failed:', error);
    operationResult.value = {
      success: false,
      message: 'Operation failed: ' + error.message,
      details: ['Please try again or contact support if the problem persists.']
    };
  } finally {
    isProcessing.value = false;
  }
};

const executeGenerateOperation = async () => {
  try {
    const result = await store.bulkGenerateRecommendations(
      props.selectedUsers,
      generateOptions.value.limit_per_user
    );

    const hasFailures = result.failed > 0;
    const hasSuccesses = result.successful > 0;

    operationResult.value = {
      success: hasSuccesses && !hasFailures,
      partial: hasSuccesses && hasFailures,
      message: hasFailures 
        ? `Operation completed with some issues: ${result.successful} successful, ${result.failed} failed`
        : `Successfully generated recommendations for ${result.successful} users`,
      details: [
        `Total users processed: ${result.total_processed}`,
        `Successful operations: ${result.successful}`,
        `Failed operations: ${result.failed}`,
        `Recommendations per user: ${generateOptions.value.limit_per_user}`
      ]
    };

    // Emit event to parent to refresh data
    emit('bulk-operation', 'generate', generateOptions.value);

  } catch (error) {
    throw new Error('Failed to generate recommendations: ' + error.message);
  }
};

const executeExportOperation = async () => {
  try {
    // For export, we need to get the data for selected users first
    const exportData = [];
    
    for (const userId of props.selectedUsers) {
      try {
        const userRec = await store.fetchUserRecommendations(userId, exportOptions.value.limit_per_user);
        exportData.push(userRec);
      } catch (error) {
        console.warn(`Failed to get recommendations for user ${userId}:`, error);
      }
    }

    if (exportOptions.value.format === 'csv') {
      // Generate CSV
      const csvContent = generateCSV(exportData);
      downloadFile(csvContent, 'selected_users_recommendations.csv', 'text/csv');
    } else {
      // Generate JSON
      const jsonContent = JSON.stringify(exportData, null, 2);
      downloadFile(jsonContent, 'selected_users_recommendations.json', 'application/json');
    }

    operationResult.value = {
      success: true,
      message: `Successfully exported data for ${exportData.length} users`,
      details: [
        `Export format: ${exportOptions.value.format.toUpperCase()}`,
        `Users exported: ${exportData.length}`,
        `Recommendations per user: ${exportOptions.value.limit_per_user}`
      ]
    };

  } catch (error) {
    throw new Error('Failed to export data: ' + error.message);
  }
};

const generateCSV = (data) => {
  const headers = [
    'User ID', 'User Email', 'User Name', 'Registration Date',
    'Recommendation Count', 'Product IDs', 'Product Names'
  ];

  const rows = data.map(user => [
    user.user_id,
    user.user_email,
    user.user_name || '',
    user.registration_date || '',
    user.recommendation_count,
    user.recommendations.map(r => r.id).join('; '),
    user.recommendations.map(r => r.name || `Product #${r.id}`).join('; ')
  ]);

  const csvContent = [headers, ...rows]
    .map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(','))
    .join('\n');

  return csvContent;
};

const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
</script>

<style scoped>
/* Modal backdrop animation */
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

/* Modal content animation */
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
</style>