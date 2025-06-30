<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage B2B Accounts</h1>
    
    <div class="mb-4 flex space-x-4">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search by company name or email..." 
        class="border rounded p-2 flex-grow"
      >
      <select v-model="statusFilter" @change="applyFilters" class="border rounded p-2">
        <option value="">All Statuses</option>
        <option v-for="status in b2bStore.statuses" :key="status" :value="status">{{ status }}</option>
      </select>
    </div>

    <div v-if="b2bStore.isLoading" class="text-center p-4">Loading accounts...</div>
    <div v-if="b2bStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ b2bStore.error }}</div>

    <BaseDataTable
      v-if="!b2bStore.isLoading && filteredAccounts.length"
      :headers="headers"
      :items="filteredAccounts"
    >
      <template #item-status="{ item }">
        <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="statusClass(item.status)">
          {{ item.status }}
        </span>
      </template>
      <template #item-created_at="{ item }">
        <span>{{ new Date(item.created_at).toLocaleDateString() }}</span>
      </template>
      <template #item-actions="{ item }">
        <button 
          v-if="item.status === 'pending'" 
          @click="approveAccount(item.id)" 
          class="text-green-600 hover:text-green-900 mr-4"
        >
          Approve
        </button>
        <button @click="openEditModal(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
        <button @click="confirmDelete(item)" class="text-red-600 hover:text-red-900">Delete</button>
      </template>
    </BaseDataTable>
    <div v-if="!b2bStore.isLoading && !filteredAccounts.length" class="text-center text-gray-500 mt-8">
        No B2B accounts found.
    </div>

    <!-- Modal for Editing B2B Account -->
    <Modal :is-open="isModalOpen" @close="closeModal">
      <h2 class="text-xl font-bold mb-4">Edit B2B Account</h2>
      <div v-if="selectedAccount" class="space-y-4">
        <p><strong>Company:</strong> {{ selectedAccount.company_name }}</p>
        <p><strong>Contact:</strong> {{ selectedAccount.contact_name }} ({{ selectedAccount.contact_email }})</p>
        <div>
          <label for="status" class="block text-sm font-medium text-gray-700">Account Status</label>
          <select id="status" v-model="selectedAccount.status" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
            <option v-for="status in b2bStore.statuses" :key="status" :value="status">{{ status }}</option>
          </select>
        </div>
        <div class="flex justify-end space-x-4">
          <button @click="closeModal" class="bg-gray-200 text-gray-700 px-4 py-2 rounded-md">Cancel</button>
          <button @click="handleSave" class="bg-indigo-600 text-white px-4 py-2 rounded-md">Save Changes</button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminB2BStore } from '@/js/stores/adminB2B';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/components/ui/Modal.vue'; // Path corrected for consistency

const b2bStore = useAdminB2BStore();

const searchQuery = ref('');
const statusFilter = ref('');
const isModalOpen = ref(false);
const selectedAccount = ref(null);

const headers = [
  { text: 'Company Name', value: 'company_name' },
  { text: 'Contact Email', value: 'contact_email' },
  { text: 'Date Joined', value: 'created_at' },
  { text: 'Status', value: 'status' },
  { text: 'Actions', value: 'actions', sortable: false },
];

onMounted(() => {
  b2bStore.fetchB2BAccounts();
});

const applyFilters = () => {
    b2bStore.fetchB2BAccounts({ status: statusFilter.value });
};

const filteredAccounts = computed(() => {
  if (!searchQuery.value) {
    return b2bStore.accounts;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return b2bStore.accounts.filter(acc => 
    acc.company_name.toLowerCase().includes(lowerCaseQuery) ||
    acc.contact_email.toLowerCase().includes(lowerCaseQuery)
  );
});

const approveAccount = (accountId) => {
    if (window.confirm('Are you sure you want to approve this account?')) {
        b2bStore.approveB2BAccount(accountId);
    }
};

const openEditModal = (account) => {
    selectedAccount.value = { ...account };
    isModalOpen.value = true;
};

const closeModal = () => {
    isModalOpen.value = false;
    selectedAccount.value = null;
};

const handleSave = async () => {
    if (selectedAccount.value) {
        await b2bStore.updateB2BAccount(selectedAccount.value.id, { status: selectedAccount.value.status });
        closeModal();
    }
};

const confirmDelete = (account) => {
    if (window.confirm(`Are you sure you want to delete the account for ${account.company_name}?`)) {
        b2bStore.deleteB2BAccount(account.id);
    }
};

const statusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  };
  return classes[status] || 'bg-gray-100';
};
</script>
