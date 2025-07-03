<!-- website/src/components/products/PersonalizedRecommendations.vue -->
<template>
  <div v-if="userStore.isAuthenticated && recommendationStore.recommendations.length > 0" class="bg-gray-50">
    <div class="mx-auto max-w-2xl py-16 px-4 sm:py-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <h2 class="text-2xl font-bold tracking-tight text-gray-900">Juste Pour Vous</h2>
      <p class="mt-2 text-sm text-gray-500">Basé sur vos achats précédents, nous pensons que vous aimerez...</p>

      <div v-if="recommendationStore.loading" class="mt-6 text-center text-gray-500">
        Chargement des recommandations...
      </div>
      
      <div v-else class="mt-6 grid grid-cols-1 gap-y-10 gap-x-6 sm:grid-cols-2 lg:grid-cols-4 xl:gap-x-8">
        <ProductCard 
          v-for="product in recommendationStore.recommendations" 
          :key="product.id" 
          :product="product" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRecommendationStore } from '@/stores/recommendations';
import { useUserStore } from '@/stores/user';
import ProductCard from '@/components/products/ProductCard.vue';

const recommendationStore = useRecommendationStore();
const userStore = useUserStore();

onMounted(() => {
  // Only fetch recommendations if the user is logged in
  if (userStore.isAuthenticated) {
    recommendationStore.fetchRecommendations();
  }
});
</script>