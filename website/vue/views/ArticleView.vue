<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="loading" class="text-center">
      <p>Chargement de l'article...</p>
    </div>
    <div v-if="error" class="text-center text-red-500">
      <p>{{ error }}</p>
    </div>
    <article v-if="article" class="prose lg:prose-xl mx-auto">
      <h1>{{ article.title }}</h1>
      <p class="text-gray-500 text-sm">Publié le {{ new Date(article.created_at).toLocaleDateString() }} par {{ article.author }}</p>
      <div v-if="article.image_url" class="my-8">
        <img :src="article.image_url" :alt="article.title" class="rounded-lg shadow-lg w-full" />
      </div>
      <!-- Sanitize the article content before rendering to prevent XSS -->
      <div v-html="sanitizedContent"></div>
    </article>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/js/api-client';
import { sanitizeHTML } from '@/security.js'; // Import the sanitizer

export default {
  name: 'ArticleView',
  setup() {
    const route = useRoute();
    const article = ref(null);
    const loading = ref(true);
    const error = ref('');

    const fetchArticle = async () => {
      try {
        const response = await apiClient.get(`/blog/articles/${route.params.slug}`);
        article.value = response.data;
      } catch (err) {
        error.value = 'Impossible de charger cet article. Veuillez réessayer plus tard.';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchArticle);

    // Create a computed property to hold the sanitized HTML
    const sanitizedContent = computed(() => {
        if (article.value && article.value.content) {
            return sanitizeHTML(article.value.content);
        }
        return '';
    });

    return {
      article,
      loading,
      error,
      sanitizedContent // Expose the sanitized content to the template
    };
  },
};
</script>
