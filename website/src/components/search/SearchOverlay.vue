<template>
  <teleport to="body">
    <transition name="search-overlay">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-black bg-opacity-50"
        @click="closeSearch"
      >
        <div class="flex items-start justify-center min-h-screen pt-16 px-4">
          <div
            class="bg-white rounded-lg shadow-xl w-full max-w-2xl"
            @click.stop
          >
            <!-- Search Header -->
            <div class="flex items-center justify-between p-4 border-b">
              <h2 class="text-lg font-semibold text-gray-900">Rechercher</h2>
              <button
                @click="closeSearch"
                class="text-gray-400 hover:text-gray-600"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Search Input -->
            <div class="p-4">
              <div class="relative">
                <input
                  ref="searchInput"
                  v-model="searchQuery"
                  type="text"
                  placeholder="Rechercher des produits, articles..."
                  class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-brand-burgundy focus:border-brand-burgundy"
                  @keyup.enter="performSearch"
                  @input="handleInput"
                />
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Search Results -->
            <div v-if="searchQuery.length > 0" class="max-h-96 overflow-y-auto">
              <!-- Loading -->
              <div v-if="isLoading" class="p-4 text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-burgundy mx-auto"></div>
                <p class="mt-2 text-gray-600">Recherche en cours...</p>
              </div>

              <!-- Results -->
              <div v-else-if="searchResults.length > 0" class="p-4">
                <h3 class="text-sm font-medium text-gray-900 mb-3">Résultats</h3>
                <div class="space-y-2">
                  <div
                    v-for="result in searchResults"
                    :key="result.id"
                    class="flex items-center p-2 hover:bg-gray-50 rounded-lg cursor-pointer"
                    @click="selectResult(result)"
                  >
                    <img
                      v-if="result.image_url"
                      :src="result.image_url"
                      :alt="result.name"
                      class="w-10 h-10 object-cover rounded-md mr-3"
                    />
                    <div class="flex-1">
                      <p class="text-sm font-medium text-gray-900">{{ result.name }}</p>
                      <p v-if="result.type" class="text-xs text-gray-500">{{ result.type }}</p>
                    </div>
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>

              <!-- No Results -->
              <div v-else class="p-4 text-center">
                <svg class="w-12 h-12 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <p class="text-gray-600">Aucun résultat trouvé</p>
                <p class="text-sm text-gray-500 mt-1">Essayez avec d'autres mots-clés</p>
              </div>
            </div>

            <!-- Popular Searches -->
            <div v-else class="p-4 border-t">
              <h3 class="text-sm font-medium text-gray-900 mb-3">Recherches populaires</h3>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="term in popularSearches"
                  :key="term"
                  @click="searchQuery = term; performSearch()"
                  class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                >
                  {{ term }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { apiClient } from '@/services/api';

const router = useRouter();

// State
const isOpen = ref(false);
const searchQuery = ref('');
const searchResults = ref([]);
const isLoading = ref(false);
const searchInput = ref(null);

// Popular searches
const popularSearches = ref([
  'Truffe noire',
  'Truffe blanche',
  'Huile de truffe',
  'Brisures de truffe',
  'Truffe d\'été'
]);

// Debounce timer
let searchTimeout = null;

// Watch for search query changes
watch(searchQuery, (newQuery) => {
  if (newQuery.length > 2) {
    // Debounce search
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      performSearch();
    }, 300);
  } else {
    searchResults.value = [];
  }
});

// Methods
function openSearch() {
  isOpen.value = true;
  nextTick(() => {
    searchInput.value?.focus();
  });
}

function closeSearch() {
  isOpen.value = false;
  searchQuery.value = '';
  searchResults.value = [];
}

function handleInput() {
  if (searchQuery.value.length === 0) {
    searchResults.value = [];
  }
}

async function performSearch() {
  if (searchQuery.value.length < 2) return;

  isLoading.value = true;
  try {
    const response = await apiClient.get('/search', {
      params: { q: searchQuery.value, limit: 8 }
    });
    searchResults.value = response.results || [];
  } catch (error) {
    console.error('Search failed:', error);
    searchResults.value = [];
  } finally {
    isLoading.value = false;
  }
}

function selectResult(result) {
  closeSearch();
  
  // Navigate based on result type
  if (result.type === 'product') {
    router.push({ name: 'ProductDetail', params: { id: result.id } });
  } else if (result.type === 'article') {
    router.push({ name: 'Article', params: { slug: result.slug } });
  } else {
    // Default to search results page
    router.push({ name: 'Search', query: { q: searchQuery.value } });
  }
}

// Expose methods for parent components
defineExpose({
  openSearch,
  closeSearch
});
</script>

<style scoped>
.search-overlay-enter-active,
.search-overlay-leave-active {
  transition: opacity 0.3s ease;
}

.search-overlay-enter-from,
.search-overlay-leave-to {
  opacity: 0;
}
</style>