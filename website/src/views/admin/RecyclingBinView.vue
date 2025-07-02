<template>
  <div class="p-4 sm:p-6 lg:p-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Recycling Bin</h1>
    <p class="text-gray-600 mb-6">
      Manage items that have been soft-deleted. You can restore them or delete them permanently.
    </p>

    <div v-if="store.isLoading && !store.items.length" class="text-center py-10">
      <p>Loading items...</p>
    </div>
    <div v-else-if="store.error" class="text-center py-10 text-red-500">
      <p>{{ store.error }}</p>
    </div>
    <div v-else-if="!store.items.length" class="text-center py-10 text-gray-500">
      <p>The recycling bin is empty.</p>
    </div>
    <div v-else class="overflow-x-auto bg-white rounded-lg shadow">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Identifier</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deleted At</th>
            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in store.items" :key="`${item.item_type}-${item.item_id}`">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">{{ item.item_type.replace('_', ' ') }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.identifier }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(item.deleted_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
              <button @click="viewLogs(item)" class="text-blue-600 hover:text-blue-900">Logs</button>
              <button @click="restoreItem(item)" class="text-green-600 hover:text-green-900">Restore</button>
              <button @click="requestHardDelete(item)" class="text-red-600 hover:text-red-900">Delete Permanently</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Confirmation Modal for Hard Delete -->
    <div v-if="showConfirmModal" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center p-4">
      <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h3 class="text-lg font-bold">Confirm Permanent Deletion</h3>
        <p class="my-4">Are you sure you want to permanently delete this item? This action cannot be undone.</p>
        <div class="flex justify-end space-x-4">
          <button @click="showConfirmModal = false" class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300">Cancel</button>
          <button @click="confirmHardDelete" class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">Confirm Delete</button>
        </div>
      </div>
    </div>

    <!-- Logs Modal -->
    <div v-if="showLogsModal" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center p-4">
      <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl">
        <h3 class="text-lg font-bold mb-4">Deletion Logs for {{ selectedItem?.identifier }}</h3>
        <div v-if="store.isLoading" class="text-center">Loading logs...</div>
        <div v-else-if="!store.logs.length" class="text-center text-gray-500">No logs found for this item.</div>
        <div v-else class="max-h-96 overflow-y-auto">
            <ul>
                <li v-for="log in store.logs" :key="log.id" class="border-b py-2">
                    <p><strong>Action:</strong> <span class="capitalize">{{ log.action.replace('_', ' ') }}</span></p>
                    <p><strong>Timestamp:</strong> {{ formatDate(log.timestamp) }}</p>
                    <p><strong>Details:</strong> {{ log.message }}</p>
                    <p><strong>Admin:</strong> {{ log.user_id }}</p>
                </li>
            </ul>
        </div>
        <div class="flex justify-end mt-6">
          <button @click="showLogsModal = false" class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300">Close</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminRecyclingBinStore } from '@/stores/adminRecyclingBin';
import { useDateFormatter } from '@/composables/useDateFormatter';

const store = useAdminRecyclingBinStore();
const { formatDate } = useDateFormatter();

const showConfirmModal = ref(false);
const showLogsModal = ref(false);
const itemToProcess = ref(null);
const selectedItem = ref(null);

onMounted(() => {
  store.fetchSoftDeletedItems();
});

function requestHardDelete(item) {
  itemToProcess.value = item;
  showConfirmModal.value = true;
}

function restoreItem(item) {
    store.restoreItem(item.item_type, item.item_id);
}

function confirmHardDelete() {
  if (itemToProcess.value) {
    store.hardDeleteItem(itemToProcess.value.item_type, itemToProcess.value.item_id);
  }
  showConfirmModal.value = false;
  itemToProcess.value = null;
}

async function viewLogs(item) {
    selectedItem.value = item;
    showLogsModal.value = true;
    await store.fetchDeletionLogs(item.item_type, item.item_id);
}
</script>
