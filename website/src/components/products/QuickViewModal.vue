<template>
  <Transition name="modal-fade">
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" @click.self="close">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto relative" role="dialog" aria-modal="true">
        <button @click="close" class="absolute top-4 right-4 text-gray-500 hover:text-gray-800" aria-label="Close modal">
          &times;
        </button>

        <div v-if="isLoading" class="p-16 text-center">
          <p>Loading product details...</p>
        </div>

        <div v-else-if="error" class="p-16 text-center text-red-600">
          <p>Sorry, we couldn't load the product details. Please try again later.</p>
        </div>

        <div v-else-if="product" class="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
          <div>
            <img :src="product.image_url || '/static/assets/placeholder.png'" :alt="product.name" class="w-full h-auto object-cover rounded-lg shadow-md">
          </div>
          <div>
            <h2 class="text-3xl font-bold">{{ product.name }}</h2>
            <p class="text-2xl font-semibold my-4">€{{ product.price.toFixed(2) }}</p>
            <div class="text-sm text-gray-600 space-y-2 mb-6" v-html="product.short_description"></div>
            
            <div class="flex items-center space-x-4 mb-6">
              <label for="quantity-qv" class="font-semibold">Quantity:</label>
              <input type="number" id="quantity-qv" v-model.number="quantity" min="1" class="w-20 p-2 border border-gray-300 rounded-md text-center">
            </div>
            
            <button @click="handleAddToCart" :disabled="isAddingToCart" class="w-full bg-black text-white font-bold py-3 px-8 rounded-md hover:bg-gray-800 transition-colors disabled:bg-gray-400">
              <span v-if="isAddingToCart">Adding...</span>
              <span v-else>Add to Cart</span>
            </button>
            
            <div class="text-center mt-4">
              <router-link :to="{ name: 'ProductDetail', params: { slug: product.slug } }" class="text-sm text-gray-600 hover:underline">
                View full details &rarr;
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue';
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api';
import { useCartStore } from '@/stores/cart';
import { useNotificationStore } from '@/stores/notification';

const props = defineProps({
  isOpen: Boolean,
  productId: [String, Number, null],
});

const emit = defineEmits(['close']);

const quantity = ref(1);
const isAddingToCart = ref(false);
const cartStore = useCartStore();
const notificationStore = useNotificationStore();

const { data: product, isLoading, error } = useApiData(
  () => {
    if (!props.productId) return Promise.resolve(null);
    return apiClient.get(`/products/${props.productId}`);
  },
  () => props.productId // Re-fetch when productId changes
);

const handleAddToCart = async () => {
  if (!product.value) return;
  isAddingToCart.value = true;
  try {
    await cartStore.addItem(props.productId, quantity.value);
    notificationStore.showNotification({ message: `${product.value.name} has been added to your cart.`, type: 'success' });
    close();
  } finally {
    isAddingToCart.value = false;
  }
};

const close = () => {
  emit('close');
};
</script>