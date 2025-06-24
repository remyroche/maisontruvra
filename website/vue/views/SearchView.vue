<template>
  <div class="bg-white">
    <div class="mx-auto max-w-7xl py-16 px-4 sm:py-24 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900">
        Résultats de recherche pour "{{ query }}"
      </h1>
      <div v-if="loading" class="mt-8 text-center">
        <p>Recherche en cours...</p>
      </div>
      <div v-else-if="error" class="mt-8 text-center text-red-500">
        <p>{{ error }}</p>
      </div>
      <div v-else-if="products.length === 0" class="mt-8 text-center">
        <p class="text-gray-500">Aucun produit ne correspond à votre recherche.</p>
      </div>
      <div v-else class="mt-6 grid grid-cols-1 gap-y-10 gap-x-6 sm:grid-cols-2 lg:grid-cols-4 xl:gap-x-8">
        <div v-for="product in products" :key="product.id" class="group relative">
          <div class="aspect-h-1 aspect-w-1 w-full overflow-hidden rounded-md bg-gray-200 lg:aspect-none group-hover:opacity-75 lg:h-80">
            <img :src="product.image_url" :alt="product.name" class="h-full w-full object-cover object-center lg:h-full lg:w-full" />
          </div>
          <div class="mt-4 flex justify-between">
            <div>
              <h3 class="text-sm text-gray-700">
                <router-link :to="{ name: 'ProductDetail', params: { id: product.id } }">
                  <span aria-hidden="true" class="absolute inset-0"></span>
                  {{ product.name }}
                </router-link>
              </h3>
            </div>
            <p class="text-sm font-medium text-gray-900">{{ product.price }} €</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../js/api-client';

const route = useRoute();
const query = ref(route.query.q || '');
const products = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchSearchResults = async (searchQuery) => {
  if (!searchQuery) {
    products.value = [];
    return;
  }
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.searchProducts(searchQuery);
    products.value = response.products || [];
  } catch (err) {
    error.value = 'Une erreur est survenue lors de la récupération des résultats.';
    console.error('Search page fetch error:', err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSearchResults(query.value);
});

watch(() => route.query.q, (newQuery) => {
  query.value = newQuery;
  fetchSearchResults(newQuery);
});
</script>
