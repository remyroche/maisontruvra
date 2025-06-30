<template>
  <div class="bg-white">
    <div class="pt-6">

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-24">
        <p class="text-lg text-gray-500">Chargement du produit...</p>
        <!-- You can add a spinner here -->
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="max-w-2xl mx-auto py-16 px-4 sm:py-24 sm:px-6 lg:max-w-7xl lg:px-8">
          <div class="text-center p-8 bg-red-50 border border-red-200 rounded-lg">
            <h3 class="text-xl font-semibold text-red-800">Une erreur est survenue</h3>
            <p class="text-red-600 mt-2">{{ error.message || 'Désolé, nous n\'avons pas pu charger les détails du produit.' }}</p>
            <button @click="fetchData" class="mt-6 px-5 py-2.5 bg-red-600 text-white font-medium rounded-lg text-sm hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-300">
              Réessayer
            </button>
          </div>
      </div>
      
      <!-- Product Info -->
      <div v-else-if="product" class="mx-auto max-w-2xl px-4 pb-16 pt-10 sm:px-6 lg:grid lg:max-w-7xl lg:grid-cols-3 lg:grid-rows-[auto,auto,1fr] lg:gap-x-8 lg:px-8 lg:pb-24 lg:pt-16">
        <!-- Main Product Layout (unchanged) -->
        <div class="lg:col-span-2 lg:border-r lg:border-gray-200 lg:pr-8">
           <h1 class="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">{{ product.name }}</h1>
        </div>
        
        <!-- Options and Add to Cart -->
        <div class="mt-4 lg:row-span-3 lg:mt-0">
          <h2 class="sr-only">Product information</h2>
          <p class="text-3xl tracking-tight text-gray-900">{{ formatCurrency(product.price) }}</p>
          
           <!-- Reviews, etc -->

          <form class="mt-10" @submit.prevent="handleAddToCart">
            <!-- Colors, Sizes etc. would go here -->
            <button type="submit" class="mt-10 flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-600 px-8 py-3 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Ajouter au panier</button>
          </form>
        </div>

        <div class="py-10 lg:col-span-2 lg:col-start-1 lg:border-r lg:border-gray-200 lg:pb-16 lg:pr-8 lg:pt-6">
          <!-- Description and details -->
          <div>
            <h3 class="sr-only">Description</h3>
            <div class="space-y-6">
              <p class="text-base text-gray-900">{{ product.description }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Not Found State -->
      <div v-else class="text-center py-24">
        <h2 class="text-2xl font-bold text-gray-900">Produit non trouvé</h2>
        <p class="text-lg text-gray-500 mt-2">Désolé, nous n'avons pas pu trouver ce produit.</p>
        <router-link :to="{ name: 'Shop' }" class="mt-6 inline-block px-5 py-2.5 bg-indigo-600 text-white font-medium rounded-lg text-sm hover:bg-indigo-700">
            Retour à la boutique
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useApiData } from '@/composables/useApiData.js';
import { useCartStore } from '@/stores/cart';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import { useNotificationStore } from '@/stores/notification';

const route = useRoute();
const cartStore = useCartStore();
const notificationStore = useNotificationStore();
const { formatCurrency } = useCurrencyFormatter();

// Use the composable for fetching data, which includes loading and error states
const { data: product, error, isLoading, fetchData } = useApiData();

const handleAddToCart = () => {
  if (product.value) {
    cartStore.addItem({ product: product.value, quantity: 1 });
    notificationStore.addNotification(`${product.value.name} a été ajouté au panier.`, 'success');
  }
};

onMounted(() => {
  // Fetch data on component mount, passing the specific API endpoint
  const slug = route.params.slug;
  fetchData(`/api/products/${slug}`);
});
</script>
