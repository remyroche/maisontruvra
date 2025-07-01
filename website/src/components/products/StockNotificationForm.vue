<template>
  <div class="p-4 bg-gray-100 rounded-md mt-6">
    <h3 class="font-semibold text-gray-800">Out of Stock</h3>
    <p class="text-sm text-gray-600 mt-1">Enter your email to be notified when this product is available again.</p>
    <form @submit.prevent="submitNotificationRequest" class="flex items-center mt-3">
      <input 
        type="email" 
        v-model="email" 
        placeholder="your.email@example.com" 
        required
        class="flex-grow border-gray-300 rounded-l-md shadow-sm focus:ring-brand-burgundy focus:border-brand-burgundy"
      >
      <button type="submit" class="bg-brand-dark-brown text-white py-2 px-4 rounded-r-md hover:bg-opacity-90 transition-colors">
        Notify Me
      </button>
    </form>
    <p v-if="message" class="text-sm mt-2" :class="isSuccess ? 'text-green-600' : 'text-red-600'">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useProductStore } from '@/stores/products';

const props = defineProps({
  productId: {
    type: Number,
    required: true
  }
});

const productStore = useProductStore();
const email = ref('');
const message = ref('');
const isSuccess = ref(false);

const submitNotificationRequest = async () => {
  if (!email.value) return;
  try {
    const response = await productStore.requestStockNotification(props.productId, email.value);
    message.value = response.message;
    isSuccess.value = true;
  } catch (error) {
    message.value = error.message || 'An error occurred. Please try again.';
    isSuccess.value = false;
  }
};
</script>
