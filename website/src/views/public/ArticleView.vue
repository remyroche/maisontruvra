<template>
  <div class="container mx-auto py-12 px-4">
    <div v-if="isLoading" class="text-center py-20">
      <p class="text-lg text-gray-600">Loading article...</p>
    </div>
    <div v-else-if="error" class="text-center py-20 bg-red-50 rounded-lg">
      <p class="text-lg text-red-700">Could not load the article. Please try again later.</p>
    </div>
    <article v-else-if="article" class="prose lg:prose-xl mx-auto">
      <h1>{{ article.title }}</h1>
      <p class="lead">{{ article.excerpt }}</p>
      <img v-if="article.cover_image" :src="article.cover_image" :alt="article.title" class="rounded-lg shadow-lg my-8 w-full">
      <div v-html="article.content"></div>
      <div class="mt-8 text-sm text-gray-500 border-t pt-4">
        <span>Published on {{ new Date(article.published_at).toLocaleDateString() }} by {{ article.author.name }}</span>
      </div>
    </article>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api';

const route = useRoute();

const { data: article, isLoading, error } = useApiData(
  () => {
    const slug = route.params.slug;
    if (!slug) return Promise.resolve(null); // Prevent fetch if no slug
    // Assuming the endpoint is /journal/:slug based on other components
    return apiClient.get(`/journal/${slug}`);
  },
  () => route.params.slug // Re-fetch when the slug prop changes
);
</script>
