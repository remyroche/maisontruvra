<!-- website/src/views/public/ArticleView.vue -->
<!-- Description: Updated to use DOMPurify to sanitize HTML content and the new API service. -->
<template>
  <div v-if="article" class="container mx-auto px-4 py-8">
    <h1 class="text-4xl font-bold mb-2">{{ article.title }}</h1>
    <p class="text-gray-500 mb-6">Published on: {{ formattedDate }}</p>
    
    <!-- Using v-html is now safe because we are sanitizing the content first -->
    <div class="prose lg:prose-xl max-w-none" v-html="sanitizedContent"></div>
  </div>
  <div v-else class="text-center py-16">
    <p>Loading article...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api'; // Use the new centralized API service
import DOMPurify from 'dompurify'; // Import DOMPurify
import { useDateFormatter } from '@/composables/useDateFormatter';

const route = useRoute();
const article = ref(null);
const { formatDate } = useDateFormatter();

// Sanitized content for rendering
const sanitizedContent = computed(() => {
  if (article.value && article.value.content) {
    // Sanitize the HTML before it is rendered. This prevents XSS attacks.
    return DOMPurify.sanitize(article.value.content);
  }
  return '';
});

const formattedDate = computed(() => {
  return article.value ? formatDate(article.value.published_at) : '';
});

onMounted(async () => {
  const articleSlug = route.params.slug; // Routes should use slug for SEO-friendly URLs
  if (!articleSlug) return;
  
  try {
    // Use the new API service method
    const response = await api.getBlogPost(articleSlug);
    article.value = response.data;
  } catch (error) {
    // The global interceptor in api.js will already show a notification.
    // We just log the error here for debugging purposes.
    console.error(`Failed to fetch article ${articleSlug}:`, error);
  }
});
</script>