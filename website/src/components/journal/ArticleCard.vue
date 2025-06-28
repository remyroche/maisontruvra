<template>
  <article class="flex flex-col items-start justify-between">
    <div class="relative w-full">
      <img :src="article.cover_image || '/static/assets/placeholder.png'" :alt="article.title" class="aspect-[16/9] w-full rounded-2xl bg-gray-100 object-cover sm:aspect-[2/1] lg:aspect-[3/2]" />
      <div class="absolute inset-0 rounded-2xl ring-1 ring-inset ring-gray-900/10" />
    </div>
    <div class="max-w-xl">
      <div class="mt-8 flex items-center gap-x-4 text-xs">
        <time :datetime="article.published_at" class="text-gray-500">{{ new Date(article.published_at).toLocaleDateString() }}</time>
        <a v-if="article.category" href="#" class="relative z-10 rounded-full bg-gray-50 px-3 py-1.5 font-medium text-gray-600 hover:bg-gray-100">{{ article.category.name }}</a>
      </div>
      <div class="group relative">
        <h3 class="mt-3 text-lg font-semibold leading-6 text-gray-900 group-hover:text-gray-600">
          <router-link :to="{ name: 'Article', params: { slug: article.slug } }">
            <span class="absolute inset-0" />
            {{ article.title }}
          </router-link>
        </h3>
        <p class="mt-5 line-clamp-3 text-sm leading-6 text-gray-600">{{ article.excerpt }}</p>
      </div>
      <div class="relative mt-8 flex items-center gap-x-4">
        <img :src="article.author.avatar_url || '/static/assets/avatar_placeholder.png'" alt="" class="h-10 w-10 rounded-full bg-gray-50" />
        <div class="text-sm leading-6">
          <p class="font-semibold text-gray-900">
            <a href="#">
              <span class="absolute inset-0" />
              {{ article.author.name }}
            </a>
          </p>
          <p class="text-gray-600">{{ article.author.role }}</p>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  article: {
    type: Object,
    required: true,
  },
});
</script>