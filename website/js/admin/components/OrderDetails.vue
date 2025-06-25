<template>
  <div v-if="order" class="space-y-6">
    <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-lg font-semibold border-b pb-2 mb-2">Order Summary</h3>
        <p><strong>Order ID:</strong> #{{ order.id }}</p>
        <p><strong>Date:</strong> {{ new Date(order.created_at).toLocaleString() }}</p>
        <p><strong>Total:</strong> ${{ order.total_amount.toFixed(2) }}</p>
        <div class="mt-4">
            <label for="status" class="block text-sm font-medium text-gray-700">Order Status</label>
            <div class="flex items-center space-x-2 mt-1">
                <select id="status" v-model="newStatus" class="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
                    <option v-for="status in ordersStore.statuses" :key="status" :value="status">{{ status }}</option>
                </select>
                <button @click="updateStatus" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Update</button>
            </div>
        </div>
    </div>
    
    <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-lg font-semibold border-b pb-2 mb-2">Customer Details</h3>
        <p><strong>Name:</strong> {{ order.customer_name }}</p>
        <p><strong>Email:</strong> {{ order.customer_email }}</p>
    </div>

    <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-lg font-semibold border-b pb-2 mb-2">Shipping Address</h3>
        <p>{{ order.shipping_address.street }}</p>
        <p>{{ order.shipping_address.city }}, {{ order.shipping_address.state }} {{ order.shipping_address.zip_code }}</p>
        <p>{{ order.shipping_address.country }}</p>
    </div>

    <div class="bg-white p-4 rounded-lg shadow">
      <h3 class="text-lg font-semibold border-b pb-2 mb-2">Items Ordered</h3>
      <ul>
        <li v-for="item in order.items" :key="item.id" class="flex justify-between items-center py-2 border-b last:border-b-0">
            <div>
                <p class="font-semibold">{{ item.product_name }}</p>
                <p class="text-sm text-gray-600">SKU: {{ item.sku }}</p>
            </div>
            <div>
                <p>{{ item.quantity }} x ${{ item.price.toFixed(2) }}</p>
            </div>
        </li>
      </ul>
    </div>

  </div>
  <div v-else class="text-center text-gray-500">
    Loading order details...
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useAdminOrdersStore } from '@/js/stores/adminOrders';

const props = defineProps({
  order: {
    type: Object,
    required: true,
  },
});

const ordersStore = useAdminOrdersStore();
const newStatus = ref(props.order?.status);

watch(() => props.order, (newOrder) => {
    if (newOrder) {
        newStatus.value = newOrder.status;
    }
}, { immediate: true });

const updateStatus = () => {
    if (newStatus.value && props.order) {
        ordersStore.updateOrderStatus(props.order.id, newStatus.value);
    }
};
</script>
