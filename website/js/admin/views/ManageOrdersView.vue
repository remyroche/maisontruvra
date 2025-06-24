<!--
 * FILENAME: website/js/admin/views/ManageOrdersView.vue
 * DESCRIPTION: View component for the 'Manage Orders' page.
 *
 * This component displays a list of all customer orders and allows admins
 * to view details for each order.
-->
<template>
  <AdminLayout>
    <div class="bg-white p-8 rounded-lg shadow-md">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800">Manage Orders</h1>
      </div>

      <!-- Loading and Error States -->
      <div v-if="orderStore.isLoading && !orderStore.orders.length" class="text-center py-10">Loading orders...</div>
      <div v-else-if="orderStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
        {{ orderStore.error }}
      </div>

      <!-- Data Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full bg-white">
          <thead class="bg-gray-800 text-white">
            <tr>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Order ID</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Customer</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Date</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-right">Total</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-center">Status</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="text-gray-700">
            <tr v-for="order in orderStore.orders" :key="order.id" class="border-b border-gray-200 hover:bg-gray-100">
              <td class="py-3 px-4">#{{ order.id }}</td>
              <td class="py-3 px-4">{{ order.customer_name }}</td>
              <td class="py-3 px-4">{{ new Date(order.created_at).toLocaleDateString() }}</td>
              <td class="py-3 px-4 text-right">€{{ order.total_amount.toFixed(2) }}</td>
              <td class="py-3 px-4 text-center">
                 <span :class="statusClass(order.status)" class="py-1 px-3 rounded-full text-xs">
                    {{ order.status }}
                 </span>
              </td>
              <td class="py-3 px-4 text-center">
                <button @click="viewOrderDetails(order)" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-2 rounded text-xs">View Details</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Order Details Modal -->
    <Modal :show="isModalOpen" @close="closeModal">
        <template #header>
            <h2 class="text-2xl font-bold">Order Details #{{ selectedOrder.id }}</h2>
        </template>
        <template #body>
            <OrderDetails v-if="selectedOrder.id" :order="selectedOrder" />
        </template>
        <template #footer>
           <button @click="closeModal" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded">Close</button>
        </template>
    </Modal>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminOrderStore } from '../../stores/adminOrders';
import AdminLayout from '../components/AdminLayout.vue';
import Modal from '../components/Modal.vue';
import OrderDetails from '../components/OrderDetails.vue';

const orderStore = useAdminOrderStore();
const isModalOpen = ref(false);
const selectedOrder = ref({});

onMounted(() => {
  orderStore.fetchOrders();
});

const viewOrderDetails = (order) => {
  selectedOrder.value = order;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedOrder.value = {};
};

const statusClass = (status) => {
    const classes = {
        'Pending': 'bg-yellow-200 text-yellow-800',
        'Processing': 'bg-blue-200 text-blue-800',
        'Shipped': 'bg-green-200 text-green-800',
        'Delivered': 'bg-purple-200 text-purple-800',
        'Cancelled': 'bg-red-200 text-red-800',
    };
    return classes[status] || 'bg-gray-200 text-gray-800';
}
</script>
