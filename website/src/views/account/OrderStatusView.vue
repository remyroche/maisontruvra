<!-- website/src/views/account/OrderStatusView.vue -->
<template>
  <div>
    <div v-if="isLoading" class="text-center py-16">
      <p class="text-gray-500">Loading order details...</p>
    </div>
    <div v-else-if="error" class="p-6 bg-red-50 rounded-lg text-center">
      <p class="text-red-700">{{ error }}</p>
    </div>
    <div v-else-if="order" class="space-y-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Order #{{ order.id }}</h1>
        <p class="text-sm text-gray-500 mt-2">
          Placed on <time :datetime="order.created_at">{{ new Date(order.created_at).toLocaleDateString() }}</time>
        </p>
      </div>

      <!-- Order Status Timeline -->
      <OrderStatusTimeline :status="order.order_status" />

      <!-- Order Summary -->
      <div class="border-t border-gray-200 pt-8">
        <h2 class="text-lg font-medium text-gray-900">Order Summary</h2>
        <div class="mt-4 bg-white border border-gray-200 rounded-lg shadow-sm">
          <ul role="list" class="divide-y divide-gray-200">
            <li v-for="item in order.items" :key="item.id" class="flex py-6 px-4 sm:px-6">
              <!-- Product Image would go here if available on the item -->
              <div class="ml-4 flex flex-1 flex-col">
                <div>
                  <div class="flex justify-between">
                    <h4 class="text-sm">
                      <router-link :to="{ name: 'ProductDetail', params: { id: item.product_id } }" class="font-medium text-gray-700 hover:text-gray-800">{{ item.product_name }}</router-link>
                    </h4>
                    <p class="ml-4 text-sm font-medium text-gray-900">{{ formatCurrency(item.price_at_purchase * item.quantity) }}</p>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">Qty: {{ item.quantity }}</p>
                </div>
              </div>
            </li>
          </ul>
          <div class="border-t border-gray-200 py-6 px-4 sm:px-6">
            <div class="flex justify-between text-base font-medium text-gray-900">
              <p>Total</p>
              <p>{{ formatCurrency(order.total_price) }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Shipping Information -->
      <div v-if="order.tracking_number" class="border-t border-gray-200 pt-8">
        <h2 class="text-lg font-medium text-gray-900">Shipping Information</h2>
        <p class="mt-4 text-sm text-gray-600">
            Tracking Number: <span class="font-medium text-gray-900">{{ order.tracking_number }}</span>
        </p>
        <a v-if="order.tracking_url" :href="order.tracking_url" target="_blank" rel="noopener noreferrer" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
            Track with carrier &rarr;
        </a>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useOrderStore } from '@/stores/orders'; // Assuming a new store for orders
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import OrderStatusTimeline from '@/components/account/OrderStatusTimeline.vue'; // A new component for the visual timeline

const route = useRoute();
const orderStore = useOrderStore();
const { formatCurrency } = useCurrencyFormatter();

const orderId = computed(() => route.params.id);
const order = computed(() => orderStore.currentOrder);
const isLoading = computed(() => orderStore.loading);
const error = computed(() => orderStore.error);

onMounted(() => {
  if (orderId.value) {
    orderStore.fetchOrderById(orderId.value);
  }
});
</script>
