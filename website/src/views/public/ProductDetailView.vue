<template>
  <div class="bg-white">
    <div class="pt-6">

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-24">
        <p class="text-lg text-gray-500">Chargement du produit...</p>
        <!-- You could add a more sophisticated spinner component here -->
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="max-w-2xl mx-auto py-16 px-4 sm:py-24 sm:px-6 lg:max-w-7xl lg:px-8">
        <div class="text-center p-8 bg-red-50 border border-red-200 rounded-lg">
          <h3 class="text-xl font-semibold text-red-800">Une erreur est survenue</h3>
          <p class="text-red-600 mt-2">{{ error }}</p>
          <button @click="fetchProductData" class="mt-6 px-5 py-2.5 bg-red-600 text-white font-medium rounded-lg text-sm hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-300">
            Réessayer
          </button>
        </div>
      </div>
      
      <!-- Product Info -->
      <div v-else-if="product" class="mx-auto max-w-2xl px-4 pb-16 pt-10 sm:px-6 lg:grid lg:max-w-7xl lg:grid-cols-3 lg:grid-rows-[auto,auto,1fr] lg:gap-x-8 lg:px-8 lg:pb-24 lg:pt-16">
        <div class="lg:col-span-2 lg:border-r lg:border-gray-200 lg:pr-8">
          <h1 class="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">{{ product.name }}</h1>
        </div>
        
        <!-- Image gallery would go on the left -->
        <div class="mt-6 lg:col-span-1 lg:row-span-2 lg:mt-0">
            <img :src="product.image_url || 'https://placehold.co/600x600/F4E9E2/7C3242?text=' + product.name" alt="Product Image" class="w-full h-full object-cover object-center rounded-lg shadow-lg">
        </div>

        <!-- Options and Add to Cart -->
        <div class="mt-4 lg:col-span-1 lg:row-span-1 lg:mt-0">
          <h2 class="sr-only">Product information</h2>
          <p class="text-3xl tracking-tight text-gray-900">{{ formatCurrency(product.price) }}</p>
          
          <!-- Add to Cart Form -->
          <form class="mt-10" @submit.prevent="handleAddToCart">
            <!-- In Stock -->
            <div v-if="product.inventory && product.inventory.quantity > 0">
              <div class="flex items-center space-x-4">
                <label for="quantity" class="text-sm font-medium text-gray-900">Quantité:</label>
                <input type="number" id="quantity" v-model.number="quantity" min="1" :max="product.inventory.quantity" class="w-20 rounded-md border-gray-300 text-center">
              </div>
              <button type="submit" class="mt-6 flex w-full items-center justify-center rounded-md border border-transparent bg-brand-burgundy px-8 py-3 text-base font-medium text-white hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-brand-burgundy focus:ring-offset-2">Ajouter au panier</button>
              <p class="text-sm text-center text-gray-500 mt-2">{{ product.inventory.quantity }} en stock</p>
            </div>
            
            <!-- Out of Stock -->
            <div v-else>
                <button type="button" disabled class="mt-6 flex w-full items-center justify-center rounded-md border border-transparent bg-gray-300 px-8 py-3 text-base font-medium text-gray-600 cursor-not-allowed">Hors stock</button>
            </div>
          </form>

          <!-- Back-in-stock notification form -->
          <StockNotificationForm 
            v-if="!product.inventory || product.inventory.quantity <= 0" 
            :product-id="product.id" 
            class="mt-4"
          />
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
        <router-link :to="{ name: 'Shop' }" class="mt-6 inline-block px-5 py-2.5 bg-brand-burgundy text-white font-medium rounded-lg text-sm hover:bg-opacity-90">
          Retour à la boutique
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useProductStore } from '@/stores/products';
import { useCartStore } from '@/stores/cart';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import StockNotificationForm from '@/components/products/StockNotificationForm.vue';
// Assuming you have a notification store for user feedback
// import { useNotificationStore } from '@/stores/notification';

const route = useRoute();
const productStore = useProductStore();
const cartStore = useCartStore();
// const notificationStore = useNotificationStore();
const { formatCurrency } = useCurrencyFormatter();

// Data state from the store
const product = computed(() => productStore.currentProduct);
const isLoading = computed(() => productStore.loading);
const error = computed(() => productStore.error);

const quantity = ref(1);

const handleAddToCart = () => {
  if (product.value) {
    cartStore.addItem({ product: product.value, quantity: quantity.value });
    // notificationStore.addNotification(`${product.value.name} a été ajouté au panier.`, 'success');
    alert(`${product.value.name} a été ajouté au panier.`); // Placeholder for notification
  }
};

const fetchProductData = () => {
  const productId = route.params.id; // Using ID as per our backend routes
  productStore.fetchProductById(productId);
};

onMounted(() => {
  fetchProductData();
});
</script>
