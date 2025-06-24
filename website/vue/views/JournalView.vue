<template>
  <div class="bg-white py-24 sm:py-32">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Le Journal</h2>
        <p class="mt-2 text-lg leading-8 text-gray-600">Découvrez nos articles sur l'upcycling, la décoration durable et nos coups de coeur.</p>
      </div>
      <div v-if="loading" class="text-center mt-16">
        <p>Chargement des articles...</p>
      </div>
      <div v-else-if="error" class="text-center mt-16 text-red-500">
        <p>{{ error }}</p>
      </div>
      <div v-else class="mx-auto mt-16 grid max-w-2xl auto-rows-fr grid-cols-1 gap-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3">
        <article v-for="post in posts" :key="post.id" class="relative isolate flex flex-col justify-end overflow-hidden rounded-2xl bg-gray-900 px-8 pb-8 pt-80 sm:pt-48 lg:pt-80">
          <img :src="post.image_url" :alt="post.title" class="absolute inset-0 -z-10 h-full w-full object-cover">
          <div class="absolute inset-0 -z-10 bg-gradient-to-t from-gray-900 via-gray-900/40"></div>
          <div class="absolute inset-0 -z-10 rounded-2xl ring-1 ring-inset ring-gray-900/10"></div>

          <div class="flex flex-wrap items-center gap-y-1 overflow-hidden text-sm leading-6 text-gray-300">
            <time :datetime="post.published_at" class="mr-8">{{ formatDate(post.published_at) }}</time>
            <div class="-ml-4 flex items-center gap-x-4">
              <svg viewBox="0 0 2 2" class="-ml-0.5 h-0.5 w-0.5 flex-none fill-white/50"><circle cx="1" cy="1" r="1" /></svg>
              <div class="flex gap-x-2.5">
                 {{ post.category.name }}
              </div>
            </div>
          </div>
          <h3 class="mt-3 text-lg font-semibold leading-6 text-white">
            <router-link :to="{ name: 'Article', params: { slug: post.slug } }">
              <span class="absolute inset-0"></span>
              {{ post.title }}
            </router-link>
          </h3>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../../js/api-client';

const posts = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    // We need to add a getBlogPosts method to our apiClient
    posts.value = await apiClient.getBlogPosts();
  } catch (err) {
    console.error('Failed to fetch blog posts:', err);
    error.value = 'Impossible de charger les articles du journal.';
  } finally {
    loading.value = false;
  }
});

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};
</script>

