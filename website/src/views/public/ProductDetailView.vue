<template>
  <div class="bg-white">
    <div v-if="isLoading" class="text-center py-40">
      <p>{{ i18n.loading }}</p>
    </div>
    <div v-else-if="error" class="text-center py-40 text-red-600">
      <p>{{ i18n.error }}</p>
    </div>
    <div v-else-if="product" class="mx-auto max-w-2xl px-4 py-16 sm:px-6 sm:py-24 lg:max-w-7xl lg:px-8">
      <div class="lg:grid lg:grid-cols-2 lg:items-start lg:gap-x-8">
        <!-- Image gallery -->
        <div class="flex flex-col-reverse">
          <!-- Image selector -->
          <div class="mx-auto mt-6 hidden w-full max-w-2xl sm:block lg:max-w-none">
            <div class="grid grid-cols-4 gap-6" aria-orientation="horizontal">
              <button v-for="image in product.images" :key="image.id" @click="selectedImage = image.url" class="relative flex h-24 cursor-pointer items-center justify-center rounded-md bg-white text-sm font-medium uppercase text-gray-900 hover:bg-gray-50 focus:outline-none focus:ring focus:ring-opacity-50 focus:ring-offset-4">
                <span class="sr-only">{{ image.alt_text }}</span>
                <span class="absolute inset-0 overflow-hidden rounded-md">
                  <img :src="image.url" :alt="image.alt_text" class="h-full w-full object-cover object-center" />
                </span>
                <span :class="[selectedImage === image.url ? 'ring-indigo-500' : 'ring-transparent', 'pointer-events-none absolute inset-0 rounded-md ring-2 ring-offset-2']" aria-hidden="true" />
              </button>
            </div>
          </div>

          <div class="aspect-h-1 aspect-w-1 w-full">
            <img :src="selectedImage" :alt="product.name" class="h-full w-full object-cover object-center sm:rounded-lg" />
          </div>
        </div>

        <!-- Product info -->
        <div class="mt-10 px-4 sm:mt-16 sm:px-0 lg:mt-0">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">{{ product.name }}</h1>

          <div class="mt-3">
            <h2 class="sr-only">Product information</h2>
            <p class="text-3xl tracking-tight text-gray-900">€{{ product.price.toFixed(2) }}</p>
          </div>

          <div class="mt-6">
            <h3 class="sr-only">{{ i18n.descriptionTitle }}</h3>
            <div class="space-y-6 text-base text-gray-700" v-html="product.description" />
          </div>

          <form @submit.prevent="handleAddToCart" class="mt-6">
            <div class="mt-10 flex">
              <button type="submit" :disabled="isAddingToCart" class="flex max-w-xs flex-1 items-center justify-center rounded-md border border-transparent bg-indigo-600 px-8 py-3 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-50 sm:w-full disabled:bg-indigo-400">
                {{ isAddingToCart ? 'Adding...' : i18n.addToCart }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Recommendations Section -->
      <ProductRecommendations :product-id="id" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api';
import { useCartStore } from '@/stores/cart';
import { useNotificationStore } from '@/stores/notification';
import ProductRecommendations from '@/components/products/ProductRecommendations.vue';
import i18nData from '@/locales/pages/product-detail.json';

const props = defineProps({
  id: { type: String, required: true },
});

const cartStore = useCartStore();
const notificationStore = useNotificationStore();
const isAddingToCart = ref(false);
const currentLang = ref('fr');
const i18n = computed(() => i18nData[currentLang.value]);

const { data: product, isLoading, error } = useApiData(
  () => apiClient.get(`/products/${props.id}`),
  () => props.id
);

const selectedImage = ref('');

watch(product, (newProduct) => {
  if (newProduct && newProduct.images && newProduct.images.length > 0) {
    selectedImage.value = newProduct.images[0].url;
  }
}, { immediate: true });

const handleAddToCart = async () => {
  if (!product.value) return;
  isAddingToCart.value = true;
  try {
    await cartStore.addItem(props.id, 1); // Assuming quantity of 1 for now
    notificationStore.showNotification({ message: `${product.value.name} has been added to your cart.`, type: 'success' });
  } finally {
    isAddingToCart.value = false;
  }
};

</script>