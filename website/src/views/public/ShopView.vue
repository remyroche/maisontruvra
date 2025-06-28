<template>
  <div class="bg-white">
    <div class="mx-auto max-w-2xl px-4 py-16 sm:px-6 sm:py-24 lg:max-w-7xl lg:px-8">
      <h2 class="text-2xl font-bold tracking-tight text-gray-900">Our Collection</h2>

      <div v-if="isLoading" class="mt-6 text-center text-gray-500">
        <p>Loading our collection...</p>
      </div>

      <div v-else-if="error" class="mt-6 text-center text-red-600">
        <p>Sorry, we couldn't load our products at this time. Please try again later.</p>
      </div>

      <div v-else-if="products && products.length" class="mt-6 grid grid-cols-1 gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-4 xl:gap-x-8">
        <ProductCard v-for="product in products" :key="product.id" :product="product" />
      </div>

      <div v-else class="mt-6 text-center text-gray-500">
        <p>No products are available at the moment. Please check back soon.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api';
import ProductCard from '@/components/products/ProductCard.vue';

const { data: products, isLoading, error } = useApiData(() => apiClient.get('/products'));
</script>