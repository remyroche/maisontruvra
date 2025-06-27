<template>
  <div class="relative">
    <button @click="isOpen = !isOpen" class="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900 focus:outline-none">
      <span>{{ currentLanguage.toUpperCase() }}</span>
      <svg class="w-5 h-5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    </button>
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div v-if="isOpen" @click.away="isOpen = false" class="origin-top-right absolute right-0 mt-2 w-24 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-20">
        <div class="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
          <a href="#" @click.prevent="setLanguage('en')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">English</a>
          <a href="#" @click.prevent="setLanguage('fr')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">Français</a>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();
const isOpen = ref(false);

const currentLanguage = computed(() => locale.value);

const setLanguage = (lang) => {
  locale.value = lang;
  isOpen.value = false;
  // You might want to save the preference to localStorage
  localStorage.setItem('preferredLanguage', lang);
};
</script>
