<template>
  <div class="bg-white p-8 rounded-lg shadow-md">
    <h1 class="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl mb-6" data-i18n="b2b.quickOrder.title">Quick Order</h1>

    <div v-if="isLoading" class="text-center py-10">
      <p data-i18n="b2b.quickOrder.loading">Loading products...</p>
    </div>

    <div v-if="error" class="text-center py-10 text-red-500">
      <p data-i18n="b2b.quickOrder.error">Failed to load products. Please try again later.</p>
    </div>

    <form v-if="!isLoading && !error" @submit.prevent="submitOrder">
      <div class="space-y-6">
        <div v-for="product in products" :key="product.id" class="grid grid-cols-12 gap-4 items-center">
          <div class="col-span-6 sm:col-span-8">
            <label :for="`product-${product.id}`" class="block text-sm font-medium text-gray-700">{{ product.name }}</label>
            <p class="text-xs text-gray-500">{{ formatPrice(product.price) }}</p>
          </div>
          <div class="col-span-6 sm:col-span-4">
            <input
              type="number"
              :id="`product-${product.id}`"
              v-model.number="orderQuantities[product.id]"
              min="0"
              placeholder="0"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
          </div>
        </div>
      </div>

      <div class="mt-8 border-t pt-6">
        <button
          type="submit"
          :disabled="isSubmitting || !hasItems"
          class="w-full flex justify-center rounded-md border border-transparent bg-indigo-600 py-3 px-4 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          <span v-if="!isSubmitting" data-i18n="b2b.quickOrder.addToCart">Add to Cart</span>
          <span v-else>
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useCartStore } from '../../stores/cart';
import apiClient from '../../api-client';

const cart = useCartStore();

// Component-specific state
const products = ref([]);
const orderQuantities = ref({});
const isLoading = ref(true);
const isSubmitting = ref(false);
const error = ref(null);

// Fetch B2B products when the component is mounted
onMounted(async () => {
  try {
    const response = await apiClient.get('/api/b2b/products'); // Assumes this endpoint exists
    products.value = response.data.products;
    // Initialize quantities for each product
    products.value.forEach(p => {
      orderQuantities.value[p.id] = 0;
    });
  } catch (err) {
    console.error("Failed to fetch B2B products:", err);
    error.value = err;
  } finally {
    isLoading.value = false;
  }
});

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(price / 100);
};

const hasItems = computed(() => {
    return Object.values(orderQuantities.value).some(qty => qty > 0);
});

// Handle the form submission
const submitOrder = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;

  const itemsToAdd = Object.entries(orderQuantities.value)
    .filter(([_, quantity]) => quantity > 0)
    .map(([productId, quantity]) => ({ product_id: parseInt(productId), quantity }));

  if (itemsToAdd.length > 0) {
    await cart.addMultipleItems(itemsToAdd);
  }

  isSubmitting.value = false;
  // Reset quantities after submission
  Object.keys(orderQuantities.value).forEach(key => {
      orderQuantities.value[key] = 0;
  });
};
</script>
