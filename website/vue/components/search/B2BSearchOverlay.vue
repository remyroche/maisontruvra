<template>
  <div v-if="b2bSearchStore.isOverlayOpen" class="relative z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity"></div>
    <div class="fixed inset-0 z-10 w-screen overflow-y-auto p-4 sm:p-6 md:p-20">
      <div @click.self="b2bSearchStore.closeOverlay()" class="flex min-h-full items-start justify-center text-center">
        <div class="relative w-full max-w-2xl transform text-left text-base transition">
          <div class="pointer-events-auto bg-white rounded-xl shadow-2xl">
            <div class="relative">
              <input
                type="text"
                :value="b2bSearchStore.query"
                @input="b2bSearchStore.setQuery($event.target.value)"
                placeholder="Rechercher par nom ou SKU..."
                class="w-full rounded-md border-0 bg-gray-100 px-4 py-4 text-gray-900 placeholder:text-gray-500 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm"
              />
              <div v-if="b2bSearchStore.loading" class="absolute top-4 right-4">
                 <svg class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </div>
            </div>
            <ul v-if="b2bSearchStore.results.length > 0" class="max-h-80 overflow-y-auto divide-y divide-gray-100">
              <li v-for="product in b2bSearchStore.results" :key="product.id">
                <router-link :to="{ name: 'B2BProductDetail', params: { id: product.id } }" @click="b2bSearchStore.closeOverlay()" class="flex items-center p-4 hover:bg-gray-50">
                  <img :src="product.image_url" :alt="product.name" class="h-16 w-16 flex-none rounded-md object-cover">
                  <div class="ml-4 flex-auto">
                    <p class="font-medium text-gray-900">{{ product.name }}</p>
                    <p class="text-sm text-gray-500">SKU: {{ product.sku }}</p>
                    <p class="text-gray-500">{{ product.price }} €</p>
                  </div>
                </router-link>
              </li>
            </ul>
            <div v-if="!b2bSearchStore.loading && b2bSearchStore.query.length > 1 && b2bSearchStore.results.length === 0" class="p-6 text-center">
              <p class="text-gray-500">Aucun résultat trouvé pour "{{ b2bSearchStore.query }}"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useB2BSearchStore } from '../../js/stores/b2bSearch';
import { onMounted, onUnmounted } from 'vue';

const b2bSearchStore = useB2BSearchStore();

const handleEsc = (e) => {
  if (e.key === 'Escape') {
    b2bSearchStore.closeOverlay();
  }
};

onMounted(() => window.addEventListener('keydown', handleEsc));
onUnmounted(() => window.removeEventListener('keydown', handleEsc));
</script>
