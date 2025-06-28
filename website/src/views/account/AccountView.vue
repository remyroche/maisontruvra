<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
    <div class="lg:grid lg:grid-cols-12 lg:gap-x-5">
      <aside class="py-6 px-2 sm:px-6 lg:col-span-3 lg:py-0 lg:px-0">
        <nav class="space-y-1">
          <router-link v-for="item in i18n.navigation" :key="item.name" :to="{ name: item.to }" :class="[$route.name === item.to ? 'bg-gray-50 text-indigo-700 hover:text-indigo-700 hover:bg-white' : 'text-gray-900 hover:text-gray-900 hover:bg-gray-50', 'group rounded-md px-3 py-2 flex items-center text-sm font-medium']" :aria-current="$route.name === item.to ? 'page' : undefined">
            <span class="truncate">{{ item.name }}</span>
          </router-link>
        </nav>
      </aside>

      <div class="space-y-6 sm:px-6 lg:col-span-9 lg:px-0">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import i18nData from '@/locales/pages/account-layout.json';

const currentLang = ref('fr');
const i18n = computed(() => i18nData[currentLang.value]);
</script>