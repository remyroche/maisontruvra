<template>
  <div class="mt-12">
    <h2 class="text-2xl font-bold tracking-tight text-gray-900">You might also like</h2>
    <p v-if="loading" class="mt-4 text-gray-500">Loading recommendations...</p>
    <p v-if="error" class="mt-4 text-red-500">{{ error }}</p>
    
    <div v-if="!loading && recommendations.length" class="mt-6 grid grid-cols-1 gap-y-10 gap-x-6 sm:grid-cols-2 lg:grid-cols-4 xl:gap-x-8">
      <ProductCard v-for="product in recommendations" :key="product.id" :product="product" />
    </div>
     <p v-if="!loading && !recommendations.length && !error" class="mt-4 text-gray-500">No recommendations available at this time.</p>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import api from '@/services/api';
import ProductCard from '@/components/products/ProductCard.vue';

export default {
  name: 'ProductRecommendations',
  components: {
    ProductCard,
  },
  props: {
    productId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const recommendations = ref([]);
    const loading = ref(false);
    const error = ref(null);

    const fetchRecommendations = async (id) => {
      if (!id) return;
      loading.value = true;
      error.value = null;
      recommendations.value = [];
      try {
        const response = await api.get(`/api/products/${id}/recommendations`);
        recommendations.value = response.data.recommendations || [];
      } catch (err) {
        console.error('Failed to fetch product recommendations:', err);
        error.value = 'Could not load recommendations.';
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchRecommendations(props.productId);
    });

    // Watch for changes in productId if the component is reused on the same page
    watch(() => props.productId, (newId) => {
      fetchRecommendations(newId);
    });

    return {
      recommendations,
      loading,
      error,
    };
  },
};
</script>
