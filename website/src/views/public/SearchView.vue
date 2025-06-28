<template>
  <div class="bg-white">
    <div class="mx-auto max-w-7xl px-6 py-16 sm:py-24 lg:px-8">
      <div v-if="isLoading" class="text-center">
        <p>{{ i18n.loading }}</p>
      </div>
      <div v-else-if="error" class="text-center text-red-600">
        <p>{{ i18n.error }}</p>
      </div>
      <div v-else>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">{{ i18n.title.replace('{query}', query) }}</h1>

        <div v-if="results && (results.products.length > 0 || results.articles.length > 0)">
          <!-- Products Section -->
          <section v-if="results.products.length > 0" class="mt-12">
            <h2 class="text-2xl font-semibold text-gray-800">{{ i18n.productsTitle }}</h2>
            <div class="mt-6 grid grid-cols-1 gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-4 xl:gap-x-8">
              <ProductCard v-for="product in results.products" :key="`prod-${product.id}`" :product="product" />
            </div>
          </section>

          <!-- Articles Section -->
          <section v-if="results.articles.length > 0" class="mt-16">
            <h2 class="text-2xl font-semibold text-gray-800">{{ i18n.articlesTitle }}</h2>
            <div class="mx-auto mt-10 grid max-w-2xl grid-cols-1 gap-x-8 gap-y-20 lg:mx-0 lg:max-w-none lg:grid-cols-3">
                <ArticleCard v-for="article in results.articles" :key="`article-${article.id}`" :article="article" />
            </div>
          </section>
        </div>

        <div v-else class="mt-12 text-center text-gray-500">
          <p>{{ i18n.noResults.replace('{query}', query) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api';
import ProductCard from '@/components/products/ProductCard.vue';
import ArticleCard from '@/components/journal/ArticleCard.vue';
import i18nData from '@/locales/pages/search.json';

const props = defineProps({
  query: { type: String, required: true, default: '' },
});

const currentLang = ref('fr');
const i18n = computed(() => i18nData[currentLang.value]);

const { data: results, isLoading, error } = useApiData(
  () => {
    if (!props.query) return Promise.resolve({ products: [], articles: [] });
    return apiClient.get(`/search?q=${encodeURIComponent(props.query)}`);
  },
  () => props.query // Re-fetch when the query prop changes
);
</script>