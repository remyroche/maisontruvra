<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Orders</h1>
    
    <div class="mb-4 flex justify-between items-center">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search by Order ID or User Email..." 
        class="border rounded p-2 w-1/3"
      >
      <div class="flex items-center space-x-4">
        <label class="flex items-center text-sm">
            <input type="checkbox" v-model="includeDeleted" @change="fetchData" class="mr-2 h-4 w-4 rounded">
            Show Deleted
        </label>
      </div>
    </div>

    <div v-if="ordersStore.isLoading" class="text-center p-4">Loading orders...</div>
    <div v-if="ordersStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ ordersStore.error }}</div>

    <BaseDataTable
      v-if="!ordersStore.isLoading && ordersStore.orders.length"
      :headers="headers"
      :items="ordersStore.orders"
    >
        <template #row="{ item, children }">
            <tr :class="{ 'bg-red-50 text-gray-500 italic': item.is_deleted }">
                <td v-for="header in headers" :key="header.value" class="px-6 py-4 whitespace-nowrap text-sm">
                    <slot :name="`item-${header.value}`" :item="item">{{ getNestedValue(item, header.value) }}</slot>
                </td>
            </tr>
        </template>
        
        <template #item-total_amount="{ item }">
            <span>${{ item.total_amount }}</span>
        </template>

        <template #item-status="{ item }">
            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="getStatusClass(item.status)">
                {{ item.status }}
            </span>
             <span v-if="item.is_deleted" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-red-200 text-red-800">Deleted</span>
        </template>
        
        <template #item-actions="{ item }">
            <div class="flex items-center space-x-2">
                <button v-if="!item.is_deleted" @click="viewOrderDetails(item.id)" class="text-indigo-600 hover:text-indigo-900 text-sm">Details</button>
                <button v-if="!item.is_deleted" @click="confirmDelete(item, 'soft')" class="text-yellow-600 hover:text-yellow-900 text-sm">Soft Delete</button>
                <button v-if="item.is_deleted" @click="restoreOrder(item.id)" class="text-green-600 hover:text-green-900 text-sm">Restore</button>
                <button @click="confirmDelete(item, 'hard')" class="text-red-600 hover:text-red-900 text-sm">Hard Delete</button>
            </div>
        </template>
    </BaseDataTable>
    
    <div v-if="!ordersStore.isLoading && !ordersStore.orders.length" class="text-center text-gray-500 mt-8">
        No orders found.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminOrdersStore } from '@/js/stores/adminOrders';
import { useRouter } from 'vue-router';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';

const ordersStore = useAdminOrdersStore();
const router = useRouter();

const searchQuery = ref('');
const includeDeleted = ref(false);

const headers = [
  { text: 'Order ID', value: 'id' },
  { text: 'User', value: 'user.email' },
  { text: 'Total', value: 'total_amount' },
  { text: 'Status', value: 'status' },
  { text: 'Date', value: 'created_at' },
  { text: 'Actions', value: 'actions', sortable: false },
];

const fetchData = () => {
  ordersStore.fetchOrders({ 
      include_deleted: includeDeleted.value,
      search: searchQuery.value 
    });
};

onMounted(fetchData);

const getNestedValue = (item, path) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], item);
}

const getStatusClass = (status) => {
    const classes = {
        'Pending': 'bg-yellow-100 text-yellow-800',
        'Shipped': 'bg-blue-100 text-blue-800',
        'Delivered': 'bg-green-100 text-green-800',
        'Cancelled': 'bg-red-100 text-red-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
};

const viewOrderDetails = (orderId) => {
    router.push({ name: 'AdminOrderDetail', params: { id: orderId }});
};

const confirmDelete = (order, type) => {
  const action = type === 'soft' ? 'soft-delete' : 'PERMANENTLY DELETE';
  if (window.confirm(`Are you sure you want to ${action} Order #${order.id}?`)) {
    const deleteAction = type === 'soft' ? ordersStore.softDeleteOrder : ordersStore.hardDeleteOrder;
    deleteAction(order.id);
  }
};

const restoreOrder = (orderId) => {
  if (window.confirm(`Are you sure you want to restore Order #${orderId}?`)) {
    ordersStore.restoreOrder(orderId);
  }
};
</script>

