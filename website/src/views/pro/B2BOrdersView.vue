<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-brand-dark-brown">Mes commandes</h1>
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

    <!-- Orders List -->
    <div class="bg-white shadow-sm rounded-lg border">
      <div v-if="isLoading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-burgundy mx-auto"></div>
        <p class="mt-2 text-gray-600">Chargement des commandes...</p>
      </div>

      <div v-else-if="error" class="p-8 text-center">
        <div class="text-red-500 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-gray-600">Erreur lors du chargement des commandes</p>
        <button @click="loadOrders" class="mt-2 text-brand-burgundy hover:underline">Réessayer</button>
      </div>

      <div v-else-if="filteredOrders.length === 0" class="p-8 text-center">
        <div class="text-gray-400 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <p class="text-gray-600">Aucune commande trouvée</p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div v-for="order in filteredOrders" :key="order.id" class="p-6 hover:bg-gray-50">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <h3 class="text-lg font-medium text-gray-900">Commande #{{ order.id }}</h3>
                <span :class="getStatusBadgeClass(order.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ getStatusText(order.status) }}
                </span>
              </div>
              <p class="mt-1 text-sm text-gray-600">{{ order.description }}</p>
              <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                <span>Commandé le {{ formatDate(order.createdAt) }}</span>
                <span>•</span>
                <span>{{ order.items.length }} article(s)</span>
                <span>•</span>
                <span class="font-medium text-gray-900">{{ formatCurrency(order.totalAmount) }}</span>
                <span v-if="order.estimatedDelivery" class="text-brand-burgundy">
                  Livraison prévue: {{ formatDate(order.estimatedDelivery) }}
                </span>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button 
                @click="viewOrder(order)"
                class="text-brand-burgundy hover:text-brand-burgundy/80 text-sm font-medium"
              >
                Voir détails
              </button>
              <button 
                v-if="order.status === 'processing'"
                @click="trackOrder(order)"
                class="text-gray-600 hover:text-gray-800 text-sm font-medium"
              >
                Suivre
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
const orders = ref([
  {
    id: 'ORD-001',
    status: 'processing',
    description: 'Commande de 25kg de truffes noires d\'hiver',
    createdAt: new Date('2024-01-15'),
    estimatedDelivery: new Date('2024-01-25'),
    totalAmount: 12500,
    items: [
      { name: 'Truffes noires d\'hiver', quantity: 25, unit: 'kg' }
    ]
  },
  {
    id: 'ORD-002',
    status: 'shipped',
    description: 'Commande de 15kg de truffes blanches d\'Alba',
    createdAt: new Date('2024-01-10'),
    estimatedDelivery: new Date('2024-01-20'),
    totalAmount: 9000,
    items: [
      { name: 'Truffes blanches d\'Alba', quantity: 15, unit: 'kg' }
    ]
  },
  {
    id: 'ORD-003',
    status: 'delivered',
    description: 'Commande de 30kg de truffes noires',
    createdAt: new Date('2024-01-05'),
    estimatedDelivery: new Date('2024-01-15'),
    totalAmount: 15000,
    items: [
      { name: 'Truffes noires', quantity: 30, unit: 'kg' }
    ]
  }
]);

// Tabs configuration
const tabs = computed(() => [
  { name: 'Toutes', count: orders.value.length },
  { name: 'En cours', count: orders.value.filter(o => o.status === 'processing').length },
  { name: 'Expédiées', count: orders.value.filter(o => o.status === 'shipped').length },
  { name: 'Livrées', count: orders.value.filter(o => o.status === 'delivered').length },
]);

// Filtered orders based on active tab
const filteredOrders = computed(() => {
  if (activeTab.value === 'all') return orders.value;
  return orders.value.filter(order => order.status === activeTab.value);
});

// Methods
const getStatusBadgeClass = (status) => {
  const classes = {
    processing: 'bg-blue-100 text-blue-800',
    shipped: 'bg-yellow-100 text-yellow-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};

const getStatusText = (status) => {
  const texts = {
    processing: 'En cours',
    shipped: 'Expédiée',
    delivered: 'Livrée',
    cancelled: 'Annulée',
  };
  return texts[status] || status;
};

const viewOrder = (order) => {
  console.log('View order:', order);
  // Navigate to order details
};

const trackOrder = (order) => {
  console.log('Track order:', order);
  // Navigate to order tracking
};

const loadOrders = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    await b2bStore.loadOrders();
    // Update orders from store
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadOrders();
});
</script>