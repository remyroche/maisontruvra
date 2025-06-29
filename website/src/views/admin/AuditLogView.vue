<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Audit Log</h1>
    
    <div class="mb-4 flex items-center space-x-4 bg-white p-3 rounded-lg shadow-sm">
      <label for="log-date" class="font-medium">Filter by Date:</label>
      <input type="date" id="log-date" v-model="selectedDate" @change="filterByDate" class="border rounded p-2">
      <button @click="clearFilter" class="text-sm text-indigo-600">Clear</button>
    </div>

    <div v-if="logStore.isLoading">Loading logs...</div>
    <div v-else>
      <BaseDataTable :headers="headers" :items="logStore.logs" />
      <!-- Pagination Controls -->
      <div class="mt-4 flex justify-between items-center">
        <span class="text-sm text-gray-700">
          Showing {{ logStore.logs.length }} of {{ logStore.pagination.total }} results
        </span>
        <div class="space-x-2">
          <button 
            @click="changePage(logStore.pagination.currentPage - 1)" 
            :disabled="!logStore.pagination.hasPrev"
            class="px-4 py-2 text-sm bg-white border rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span class="px-4 py-2 text-sm bg-white border rounded">
            Page {{ logStore.pagination.currentPage }} of {{ logStore.pagination.pages }}
          </span>
          <button 
            @click="changePage(logStore.pagination.currentPage + 1)" 
            :disabled="!logStore.pagination.hasNext"
            class="px-4 py-2 text-sm bg-white border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import BaseDataTable from '@/components/ui/BaseDataTable.vue';
import api from '@/services/api';

const logStore = useAdminAuditLogStore();
const selectedDate = ref(null);

const headers = [
    { text: 'Timestamp', value: 'timestamp' },
    { text: 'Staff User', value: 'admin_user_email' },
    { text: 'Action', value: 'action' },
    { text: 'Details', value: 'details' },
];

onMounted(() => {
    logStore.fetchLogs();
});

const changePage = (page) => {
    logStore.fetchLogs(page, selectedDate.value);
};

const filterByDate = () => {
    logStore.fetchLogs(1, selectedDate.value);
};

const clearFilter = () => {
    selectedDate.value = null;
    logStore.fetchLogs(1);
};
</script>
