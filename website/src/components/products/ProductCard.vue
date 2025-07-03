<!-- website/src/components/products/ProductCard.vue -->
<template>
  <div class="group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white">
    <div class="aspect-w-3 aspect-h-4 bg-gray-200 group-hover:opacity-75 sm:aspect-none sm:h-96">
      <img :src="product.image_url || 'https://placehold.co/400x500/F4E9E2/7C3242?text=Image'" 
           :alt="product.name" 
           class="h-full w-full object-cover object-center sm:h-full sm:w-full" />
    </div>
    <div class="flex flex-1 flex-col space-y-2 p-4">
      <h3 class="text-sm font-medium text-gray-900">
        <router-link :to="{ name: 'ProductDetail', params: { id: product.id } }">
          <span aria-hidden="true" class="absolute inset-0" />
          {{ product.name }}
        </router-link>
      </h3>
      <p class="text-sm text-gray-500">{{ product.category_name || 'Catégorie' }}</p>
      <div class="flex flex-1 flex-col justify-end">
        <p class="text-base font-medium text-gray-900">{{ formatCurrency(product.price) }}</p>
      </div>
    </div>
    
    <!-- --- WISHLIST BUTTON --- -->
    <div v-if="userStore.isAuthenticated" class="absolute top-2 right-2 z-10">
      <AddToWishlistButton :product-id="product.id" />
    </div>
    <!-- --------------------- -->

  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import { useUserStore } from '@/stores/user';
import AddToWishlistButton from '@/components/products/AddToWishlistButton.vue';

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
});

const { formatCurrency } = useCurrencyFormatter();
const userStore = useUserStore();
</script>
