<!-- website/src/components/products/AddToWishlistButton.vue -->
<template>
  <button @click="toggleWishlist" type="button" 
          :disabled="isLoading"
          class="p-3 text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 rounded-full transition-colors duration-200"
          :class="{ 'text-red-500': isInWishlist }">
    <span class="sr-only">Add to wishlist</span>
    <HeartIcon :class="[isInWishlist ? 'fill-current' : 'stroke-current', 'h-6 w-6']" />
  </button>
</template>

<script setup>
import { ref, watch, onMounted, defineProps } from 'vue';
import { HeartIcon } from '@heroicons/vue/24/outline'; // Use outline for default, fill for active
import { useUserStore } from '@/stores/user'; // Assuming user store handles wishlist logic

const props = defineProps({
  productId: {
    type: [Number, String],
    required: true,
  },
});

const userStore = useUserStore();
const isLoading = ref(false);
const isInWishlist = ref(false);

// Check the initial wishlist status when the component mounts
const checkWishlistStatus = async () => {
    if (!props.productId) return;
    // Assuming the user store has a method to check if an item is in the wishlist
    isInWishlist.value = await userStore.isProductInWishlist(props.productId);
};

const toggleWishlist = async () => {
  isLoading.value = true;
  try {
    if (isInWishlist.value) {
      await userStore.removeFromWishlist(props.productId);
      isInWishlist.value = false;
      // Optionally show notification: "Removed from wishlist"
    } else {
      await userStore.addToWishlist(props.productId);
      isInWishlist.value = true;
      // Optionally show notification: "Added to wishlist"
    }
  } catch (error) {
    console.error("Failed to update wishlist:", error);
    // Optionally show an error notification
  } finally {
    isLoading.value = false;
  }
};

// Watch for the productId prop to change and re-check the status
watch(() => props.productId, checkWishlistStatus);

// Initial check on mount
onMounted(() => {
  checkWishlistStatus();
});
</script>
