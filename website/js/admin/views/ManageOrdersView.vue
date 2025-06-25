<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Orders</h1>
    
    <div class="mb-4 flex space-x-4">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search by ID or customer email..." 
        class="border rounded p-2 flex-grow"
      >
      <select v-model="statusFilter" @change="applyFilters" class="border rounded p-2">
        <option value="">All Statuses</option>
        <option v-for="status in ordersStore.statuses" :key="status" :value="status">{{ status }}</option>
      </select>
    </div>

    <div v-if="ordersStore.isLoading" class="text-center p-4">Loading orders...</div>
    <div v-if="ordersStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ ordersStore.error }}</div>

    <BaseDataTable
      v-if="!ordersStore.isLoading && filteredOrders.length"
      :headers="headers"
      :items="filteredOrders"
    >
      <template #item-id="{ item }">
        <strong>#{{ item.id }}</strong>
      </template>
      <template #item-total_amount="{ item }">
        <span>${{ item.total_amount.toFixed(2) }}</span>
      </template>
       <template #item-created_at="{ item }">
        <span>{{ new Date(item.created_at).toLocaleDateString() }}</span>
      </template>
      <template #item-status="{ item }">
        <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="statusClass(item.status)">
          {{ item.status }}
        </span>
      </template>
      <template #item-actions="{ item }">
        <button @click="openDetailsModal(item.id)" class="text-indigo-600 hover:text-indigo-900">View Details</button>
      </template>
    </BaseDataTable>
    <div v-if="!ordersStore.isLoading && !filteredOrders.length" class="text-center text-gray-500 mt-8">
        No orders found.
    </div>

    <!-- Modal for Order Details -->
    <Modal :is-open="isModalOpen" @close="closeModal">
        <OrderDetails v-if="ordersStore.order" :order="ordersStore.order" />
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminOrdersStore } from '@/js/stores/adminOrders';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/js/admin/components/Modal.vue';
import OrderDetails from '@/js/admin/components/OrderDetails.vue';

const ordersStore = useAdminOrdersStore();

const searchQuery = ref('');
const statusFilter = ref('');
const isModalOpen = ref(false);

const headers = [
  { text: 'Order ID', value: 'id' },
  { text: 'Customer', value: 'customer_name' },
  { text: 'Date', value: 'created_at' },
  { text: 'Total', value: 'total_amount' },
  { text: 'Status', value: 'status' },
  { text: 'Actions', value: 'actions', sortable: false },
];

onMounted(() => {
  ordersStore.fetchOrders();
});

const applyFilters = () => {
    ordersStore.fetchOrders({ status: statusFilter.value });
};

const filteredOrders = computed(() => {
  if (!searchQuery.value) {
    return ordersStore.orders;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return ordersStore.orders.filter(order => 
    order.customer_email.toLowerCase().includes(lowerCaseQuery) ||
    order.id.toString().includes(lowerCaseQuery)
  );
});

const openDetailsModal = (orderId) => {
    ordersStore.fetchOrderDetails(orderId);
    isModalOpen.value = true;
};

const closeModal = () => {
    isModalOpen.value = false;
    ordersStore.order = null; // Clear the selected order
};

const statusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    paid: 'bg-blue-100 text-blue-800',
    shipped: 'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    refunded: 'bg-gray-100 text-gray-800',
  };
  return classes[status] || 'bg-gray-100';
};
</script>

