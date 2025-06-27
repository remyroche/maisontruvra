<template>
  <div v-if="recommendations.length > 0" class="mt-12">
    <h2 class="text-2xl font-semibold text-gray-800 mb-4">You Might Also Like</h2>
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
      <div v-for="product in recommendations" :key="product.id" class="border rounded-lg p-4 text-center hover:shadow-lg transition-shadow">
        <a :href="`/products/${product.slug}`">
          <img :src="product.image_url || '/static/assets/placeholder.png'" :alt="product.name" class="w-full h-40 object-cover rounded-md mb-2">
          <h3 class="font-medium text-gray-700">{{ product.name }}</h3>
          <p class="text-gray-900 font-semibold">€{{ product.price }}</p>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { apiClient } from '../../../api-client';

const props = defineProps({
  productId: {
    type: String,
    required: true
  }
});

const recommendations = ref([]);

async function fetchRecommendations(id) {
  if (!id) return;
  try {
    const response = await apiClient.get(`/products/${id}/recommendations`);
    recommendations.value = response.data;
  } catch (error) {
    console.error("Failed to fetch product recommendations:", error);
  }
}

onMounted(() => {
  fetchRecommendations(props.productId);
});

// Watch for changes if the product ID can change on the same page
watch(() => props.productId, (newId) => {
    fetchRecommendations(newId);
});
</script>
