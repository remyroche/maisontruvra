<template>
  <div class="bg-white rounded-lg shadow-sm border p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Mode de livraison</h3>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-burgundy"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-600 mb-2">
        <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <button 
        @click="fetchDeliveryMethods"
        class="px-4 py-2 bg-brand-burgundy text-white rounded-md hover:bg-opacity-90"
      >
        Réessayer
      </button>
    </div>

    <!-- Delivery Methods -->
    <div v-else class="space-y-3">
      <div 
        v-for="method in deliveryMethods" 
        :key="method.id"
        class="border rounded-lg p-4 cursor-pointer transition-colors"
        :class="{
          'border-brand-burgundy bg-brand-cream': selectedMethod?.id === method.id,
          'border-gray-200 hover:border-gray-300': selectedMethod?.id !== method.id,
          'opacity-50 cursor-not-allowed': !method.available
        }"
        @click="method.available && selectMethod(method)"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start flex-1">
            <input 
              type="radio" 
              :checked="selectedMethod?.id === method.id"
              :disabled="!method.available"
              class="mt-1 text-brand-burgundy focus:ring-brand-burgundy"
              readonly
            >
            <div class="ml-3 flex-1">
              <div class="flex items-center justify-between">
                <h4 class="font-medium text-gray-900">{{ method.name }}</h4>
                <div class="text-right">
                  <span v-if="method.price > 0" class="font-semibold text-gray-900">
                    {{ formatPrice(method.price) }}
                  </span>
                  <span v-else class="font-semibold text-green-600">Gratuit</span>
                </div>
              </div>
              
              <p class="text-sm text-gray-600 mt-1">{{ method.description }}</p>
              
              <!-- Delivery Time -->
              <div class="flex items-center mt-2 text-sm">
                <svg class="w-4 h-4 text-gray-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-600">{{ method.delivery_time }}</span>
              </div>

              <!-- Special Features -->
              <div v-if="method.features && method.features.length" class="mt-2">
                <div class="flex flex-wrap gap-1">
                  <span 
                    v-for="feature in method.features" 
                    :key="feature"
                    class="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                  >
                    {{ feature }}
                  </span>
                </div>
              </div>

              <!-- Availability Notice -->
              <div v-if="!method.available" class="mt-2">
                <span class="inline-flex items-center px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                  {{ method.unavailable_reason || 'Non disponible' }}
                </span>
              </div>

              <!-- Estimated Delivery Date -->
              <div v-if="method.estimated_delivery && method.available" class="mt-2 text-sm">
                <span class="text-gray-500">Livraison estimée : </span>
                <span class="font-medium text-gray-900">{{ formatDate(method.estimated_delivery) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No delivery methods available -->
      <div v-if="deliveryMethods.length === 0" class="text-center py-8 text-gray-500">
        <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p>Aucun mode de livraison disponible pour cette adresse.</p>
      </div>
    </div>

    <!-- Delivery Information -->
    <div v-if="selectedMethod" class="mt-6 p-4 bg-blue-50 rounded-lg">
      <h4 class="font-medium text-blue-900 mb-2">Informations de livraison</h4>
      <div class="text-sm text-blue-800 space-y-1">
        <p v-if="selectedMethod.tracking_available">
          <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Suivi de colis inclus
        </p>
        <p v-if="selectedMethod.insurance_included">
          <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Assurance incluse
        </p>
        <p v-if="selectedMethod.signature_required">
          <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          Signature requise
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { apiClient } from '@/services/api';

const props = defineProps({
  shippingAddress: {
    type: Object,
    default: null
  },
  cartTotal: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['method-selected']);

// State
const deliveryMethods = ref([]);
const selectedMethod = ref(null);
const isLoading = ref(false);
const error = ref(null);

// Computed
const hasValidSelection = computed(() => !!selectedMethod.value);

// Methods
async function fetchDeliveryMethods() {
  if (!props.shippingAddress) return;
  
  isLoading.value = true;
  error.value = null;
  
  try {
    const params = {
      address_id: props.shippingAddress.id,
      cart_total: props.cartTotal
    };
    
    const response = await apiClient.get('/delivery/methods', { params });
    deliveryMethods.value = response.delivery_methods || [];
    
    // Auto-select the first available method if none selected
    if (!selectedMethod.value && deliveryMethods.value.length > 0) {
      const firstAvailable = deliveryMethods.value.find(method => method.available);
      if (firstAvailable) {
        selectMethod(firstAvailable);
      }
    }
  } catch (err) {
    console.error('Failed to fetch delivery methods:', err);
    error.value = 'Impossible de charger les modes de livraison. Veuillez réessayer.';
  } finally {
    isLoading.value = false;
  }
}

function selectMethod(method) {
  if (!method.available) return;
  
  selectedMethod.value = method;
  emit('method-selected', method);
}

function formatPrice(price) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(price);
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
}

// Watch for address changes
watch(() => props.shippingAddress, (newAddress) => {
  if (newAddress) {
    selectedMethod.value = null; // Reset selection when address changes
    fetchDeliveryMethods();
  }
}, { immediate: true });

// Lifecycle
onMounted(() => {
  if (props.shippingAddress) {
    fetchDeliveryMethods();
  }
});

// Expose methods for parent component
defineExpose({
  selectedMethod: computed(() => selectedMethod.value),
  hasValidSelection,
  refresh: fetchDeliveryMethods
});
</script>