<template>
  <button
    @click="addToCart"
    :disabled="isLoading"
    type="button"
    class="flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-600 px-8 py-3 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
  >
    <span v-if="!isLoading" data-i18n="product.addToCart">Add to bag</span>
    <span v-else>
      <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
  </button>
</template>

<script setup>
import { ref } from 'vue';
import { useCartStore } from '../../stores/cart';

// Define the component's props
const props = defineProps({
  productId: {
    type: [Number, String],
    required: true,
  },
});

// Loading state for visual feedback
const isLoading = ref(false);

// Initialize the Pinia cart store
const cart = useCartStore();

// Function to handle the button click
const addToCart = async () => {
  if (isLoading.value) return;

  isLoading.value = true;
  try {
    // Call the 'addItem' action from our Pinia store
    await cart.addItem(props.productId, 1);
    // Optionally, you can add a success notification here
  } catch (error) {
    console.error("Error adding item from component:", error);
    // Optionally, show an error notification
  } finally {
    isLoading.value = false;
  }
};
</script>
