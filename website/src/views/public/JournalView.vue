<template>
  <div class="bg-white py-24 sm:py-32">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ i18n.title }}</h2>
        <p class="mt-2 text-lg leading-8 text-gray-600">{{ i18n.subtitle }}</p>
      </div>

      <div v-if="isLoading" class="mt-16 text-center text-gray-500">
        <p>{{ i18n.loading }}</p>
      </div>
      <div v-else-if="error" class="mt-16 text-center text-red-600">
        <p>{{ i18n.error }}</p>
      </div>
      <div v-else-if="articles && articles.length" class="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-x-8 gap-y-20 lg:mx-0 lg:max-w-none lg:grid-cols-3">
        <ArticleCard v-for="article in articles" :key="article.id" :article="article" />
      </div>
      <div v-else class="mt-16 text-center text-gray-500">
        <p>{{ i18n.noArticles }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api';
import ArticleCard from '@/components/journal/ArticleCard.vue';
import i18nData from '@/locales/pages/journal.json';

const currentLang = ref('fr');
const i18n = computed(() => i18nData[currentLang.value]);

const { data: articles, isLoading, error } = useApiData(() => apiClient.get('/journal'));
</script>