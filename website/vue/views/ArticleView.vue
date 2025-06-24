<template>
  <div class="bg-white px-6 py-32 lg:px-8">
    <div v-if="loading" class="text-center">
      <p>Chargement de l'article...</p>
    </div>
    <div v-else-if="error" class="text-center text-red-500">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="post" class="mx-auto max-w-3xl text-base leading-7 text-gray-700">
      <p class="text-base font-semibold leading-7 text-indigo-600">{{ post.category.name }}</p>
      <h1 class="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ post.title }}</h1>
      <p class="mt-6 text-xl leading-8">{{ post.excerpt }}</p>
      <figure class="mt-16">
        <img class="aspect-video rounded-xl bg-gray-50 object-cover" :src="post.image_url" :alt="post.title">
        <figcaption class="mt-4 flex gap-x-2 text-sm leading-6 text-gray-500">
          Publié le {{ formatDate(post.published_at) }}
        </figcaption>
      </figure>
      <!-- This div now renders the sanitized HTML content -->
      <div class="mt-10 prose lg:prose-xl max-w-none" v-html="sanitizedContent"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../js/api-client';
import DOMPurify from 'dompurify'; // Import DOMPurify

const route = useRoute();
const post = ref(null);
const loading = ref(true);
const error = ref(null);

// Create a computed property to hold the sanitized HTML
const sanitizedContent = computed(() => {
  if (post.value && post.value.content) {
    // Sanitize the content before rendering
    return DOMPurify.sanitize(post.value.content);
  }
  return '';
});

const fetchPost = async (slug) => {
  loading.value = true;
  error.value = null;
  post.value = null;
  try {
    post.value = await apiClient.getBlogPostBySlug(slug);
  } catch (err) {
    console.error('Failed to fetch post:', err);
    error.value = "L'article demandé n'a pas pu être chargé.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchPost(route.params.slug);
});

watch(() => route.params.slug, (newSlug) => {
  if (newSlug) {
    fetchPost(newSlug);
  }
});

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};
</script>
