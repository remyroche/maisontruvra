<!-- website/src/components/products/RecentlyViewed.vue -->
<template>
  <div v-if="productStore.recentlyViewed.length > 0" class="bg-white">
    <div class="mx-auto max-w-2xl py-16 px-4 sm:py-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <h2 class="text-2xl font-bold tracking-tight text-gray-900">Récemment Consultés</h2>

      <div v-if="productStore.recentlyViewedLoading" class="mt-6 text-center text-gray-500">
        Chargement...
      </div>
      
      <div v-else class="mt-6 grid grid-cols-1 gap-y-10 gap-x-6 sm:grid-cols-2 lg:grid-cols-4 xl:gap-x-8">
        <ProductCard 
          v-for="product in productStore.recentlyViewed" 
          :key="product.id" 
          :product="product" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useProductStore } from '@/stores/products';
import ProductCard from '@/components/products/ProductCard.vue'; // Re-use the existing product card

const productStore = useProductStore();

onMounted(() => {
  // Fetch the full product details for the recently viewed items
  productStore.fetchRecentlyViewedProducts();
});
</script>