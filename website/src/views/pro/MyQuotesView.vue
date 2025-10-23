<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-brand-dark-brown">Mes devis</h1>
      <router-link 
        to="/pro/request-quote" 
        class="bg-brand-burgundy text-white px-4 py-2 rounded-lg hover:bg-brand-burgundy/90 transition-colors"
      >
        Nouveau devis
      </router-link>
    </div>

    <!-- Filter Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          @click="activeTab = tab.name"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.name
              ? 'border-brand-burgundy text-brand-burgundy'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.name }}
          <span v-if="tab.count" class="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Quotes List -->
    <div class="bg-white shadow-sm rounded-lg border">
      <div v-if="isLoading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-burgundy mx-auto"></div>
        <p class="mt-2 text-gray-600">Chargement des devis...</p>
      </div>

      <div v-else-if="error" class="p-8 text-center">
        <div class="text-red-500 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-gray-600">Erreur lors du chargement des devis</p>
        <button @click="loadQuotes" class="mt-2 text-brand-burgundy hover:underline">Réessayer</button>
      </div>

      <div v-else-if="filteredQuotes.length === 0" class="p-8 text-center">
        <div class="text-gray-400 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-gray-600">Aucun devis trouvé</p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div v-for="quote in filteredQuotes" :key="quote.id" class="p-6 hover:bg-gray-50">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <h3 class="text-lg font-medium text-gray-900">Devis #{{ quote.id }}</h3>
                <span :class="getStatusBadgeClass(quote.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ getStatusText(quote.status) }}
                </span>
              </div>
              <p class="mt-1 text-sm text-gray-600">{{ quote.description }}</p>
              <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                <span>Créé le {{ formatDate(quote.createdAt) }}</span>
                <span>•</span>
                <span>{{ quote.items.length }} article(s)</span>
                <span>•</span>
                <span class="font-medium text-gray-900">{{ formatCurrency(quote.totalAmount) }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button 
                @click="viewQuote(quote)"
                class="text-brand-burgundy hover:text-brand-burgundy/80 text-sm font-medium"
              >
                Voir détails
              </button>
              <button 
                v-if="quote.status === 'pending'"
                @click="editQuote(quote)"
                class="text-gray-600 hover:text-gray-800 text-sm font-medium"
              >
                Modifier
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useB2BStore } from '@/stores/b2b';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import { useDateFormatter } from '@/composables/useDateFormatter';

const b2bStore = useB2BStore();
const { formatCurrency } = useCurrencyFormatter();
const { formatDate } = useDateFormatter();

// State
const activeTab = ref('all');
const isLoading = ref(false);
const error = ref(null);

// Mock data - in real app, this would come from the store
const quotes = ref([
  {
    id: 'QT-001',
    status: 'pending',
    description: 'Demande de devis pour 50kg de truffes noires d\'hiver',
    createdAt: new Date('2024-01-15'),
    totalAmount: 25000,
    items: [
      { name: 'Truffes noires d\'hiver', quantity: 50, unit: 'kg' }
    ]
  },
  {
    id: 'QT-002',
    status: 'approved',
    description: 'Devis pour 25kg de truffes blanches d\'Alba',
    createdAt: new Date('2024-01-10'),
    totalAmount: 15000,
    items: [
      { name: 'Truffes blanches d\'Alba', quantity: 25, unit: 'kg' }
    ]
  },
  {
    id: 'QT-003',
    status: 'rejected',
    description: 'Demande de devis pour 100kg de truffes noires',
    createdAt: new Date('2024-01-05'),
    totalAmount: 50000,
    items: [
      { name: 'Truffes noires', quantity: 100, unit: 'kg' }
    ]
  }
]);

// Tabs configuration
const tabs = computed(() => [
  { name: 'Tous', count: quotes.value.length },
  { name: 'En attente', count: quotes.value.filter(q => q.status === 'pending').length },
  { name: 'Approuvés', count: quotes.value.filter(q => q.status === 'approved').length },
  { name: 'Rejetés', count: quotes.value.filter(q => q.status === 'rejected').length },
]);

// Filtered quotes based on active tab
const filteredQuotes = computed(() => {
  if (activeTab.value === 'all') return quotes.value;
  return quotes.value.filter(quote => quote.status === activeTab.value);
});

// Methods
const getStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};

const getStatusText = (status) => {
  const texts = {
    pending: 'En attente',
    approved: 'Approuvé',
    rejected: 'Rejeté',
  };
  return texts[status] || status;
};

const viewQuote = (quote) => {
  console.log('View quote:', quote);
  // Navigate to quote details
};

const editQuote = (quote) => {
  console.log('Edit quote:', quote);
  // Navigate to edit quote
};

const loadQuotes = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    await b2bStore.loadQuotes();
    // Update quotes from store
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadQuotes();
});
</script>