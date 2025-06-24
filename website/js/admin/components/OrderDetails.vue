<!--
 * FILENAME: website/js/admin/components/OrderDetails.vue
 * DESCRIPTION: Component to display the detailed information of a single order.
 *
 * This component is used within a modal to show everything about an order,
 * including customer details, shipping address, and the list of products ordered.
-->
<template>
  <div class="text-sm text-gray-700">
    <!-- Customer & Order Info -->
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div>
        <h3 class="font-bold text-gray-800">Customer</h3>
        <p>{{ order.customer_name }}</p>
        <p>{{ order.customer_email }}</p>
      </div>
      <div>
        <h3 class="font-bold text-gray-800">Shipping Address</h3>
        <p>{{ order.shipping_address.street }}</p>
        <p>{{ order.shipping_address.city }}, {{ order.shipping_address.postal_code }}</p>
        <p>{{ order.shipping_address.country }}</p>
      </div>
    </div>

    <!-- Order Items -->
    <div>
      <h3 class="font-bold text-gray-800 mb-2">Items Ordered</h3>
      <div class="border rounded-lg overflow-hidden">
        <table class="min-w-full">
          <thead class="bg-gray-100">
            <tr>
              <th class="py-2 px-3 text-left">Product</th>
              <th class="py-2 px-3 text-center">Quantity</th>
              <th class="py-2 px-3 text-right">Price</th>
              <th class="py-2 px-3 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in order.items" :key="item.id" class="border-t">
              <td class="py-2 px-3">{{ item.product_name }}</td>
              <td class="py-2 px-3 text-center">{{ item.quantity }}</td>
              <td class="py-2 px-3 text-right">€{{ item.unit_price.toFixed(2) }}</td>
              <td class="py-2 px-3 text-right">€{{ (item.quantity * item.unit_price).toFixed(2) }}</td>
            </tr>
          </tbody>
          <tfoot class="font-bold bg-gray-50">
            <tr>
                <td colspan="3" class="py-2 px-3 text-right">Subtotal</td>
                <td class="py-2 px-3 text-right">€{{ order.subtotal.toFixed(2) }}</td>
            </tr>
             <tr>
                <td colspan="3" class="py-2 px-3 text-right">Shipping</td>
                <td class="py-2 px-3 text-right">€{{ order.shipping_cost.toFixed(2) }}</td>
            </tr>
             <tr>
                <td colspan="3" class="py-2 px-3 text-right text-lg">Total</td>
                <td class="py-2 px-3 text-right text-lg">€{{ order.total_amount.toFixed(2) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Status Update -->
    <div class="mt-6">
        <label for="order_status" class="block font-bold text-gray-800 mb-2">Update Order Status</label>
        <div class="flex">
            <select id="order_status" v-model="newStatus" class="flex-grow border-gray-300 rounded-l-md shadow-sm">
                <option>Pending</option>
                <option>Processing</option>
                <option>Shipped</option>
                <option>Delivered</option>
                <option>Cancelled</option>
            </select>
            <button @click="updateStatus" :disabled="orderStore.isLoading" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-r-md">
                {{ orderStore.isLoading ? 'Updating...' : 'Update' }}
            </button>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAdminOrderStore } from '../../stores/adminOrders';

const props = defineProps({
  order: {
    type: Object,
    required: true
  }
});

const orderStore = useAdminOrderStore();
const newStatus = ref(props.order.status);

const updateStatus = async () => {
    if (newStatus.value !== props.order.status) {
        await orderStore.updateOrderStatus(props.order.id, newStatus.value);
    }
}
</script>
