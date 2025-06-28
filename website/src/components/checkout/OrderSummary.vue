<template>
  <div class="bg-white rounded-lg shadow-sm border p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Récapitulatif de commande</h3>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-burgundy"></div>
    </div>

    <!-- Empty Cart -->
    <div v-else-if="!cart || !cart.items || cart.items.length === 0" class="text-center py-8">
      <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 6M7 13l-1.5-6m0 0L4 5M7 13h10m0 0l1.5 6M17 13l1.5 6" />
      </svg>
      <p class="text-gray-500">Votre panier est vide</p>
      <router-link 
        to="/shop" 
        class="inline-block mt-4 px-4 py-2 bg-brand-burgundy text-white rounded-md hover:bg-opacity-90"
      >
        Continuer mes achats
      </router-link>
    </div>

    <!-- Cart Items -->
    <div v-else>
      <!-- Items List -->
      <div class="space-y-4 mb-6">
        <div 
          v-for="item in cart.items" 
          :key="item.id"
          class="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg"
        >
          <!-- Product Image -->
          <div class="flex-shrink-0">
            <img 
              :src="item.product.image_url || '/placeholder-product.jpg'" 
              :alt="item.product.name"
              class="w-16 h-16 object-cover rounded-md"
            >
          </div>

          <!-- Product Details -->
          <div class="flex-1 min-w-0">
            <h4 class="font-medium text-gray-900 truncate">{{ item.product.name }}</h4>
            <p v-if="item.product.variant" class="text-sm text-gray-600">{{ item.product.variant }}</p>
            <p v-if="item.product.weight" class="text-sm text-gray-600">{{ item.product.weight }}</p>
            
            <!-- Quantity and Price -->
            <div class="flex items-center justify-between mt-2">
              <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-600">Quantité:</span>
                <span class="font-medium">{{ item.quantity }}</span>
              </div>
              <div class="text-right">
                <div class="font-medium text-gray-900">{{ formatPrice(item.total_price) }}</div>
                <div v-if="item.unit_price !== item.discounted_price" class="text-sm text-gray-500">
                  <span class="line-through">{{ formatPrice(item.unit_price * item.quantity) }}</span>
                  <span class="text-green-600 ml-1">-{{ calculateDiscount(item) }}%</span>
                </div>
              </div>
            </div>

            <!-- Special Notes -->
            <div v-if="item.notes" class="mt-2 text-sm text-gray-600 italic">
              Note: {{ item.notes }}
            </div>
          </div>
        </div>
      </div>

      <!-- Promo Code Section -->
      <div class="mb-6 p-4 bg-gray-50 rounded-lg">
        <div v-if="!showPromoForm && !cart.promo_code" class="text-center">
          <button 
            @click="showPromoForm = true"
            class="text-brand-burgundy hover:text-opacity-80 font-medium"
          >
            Avez-vous un code promo ?
          </button>
        </div>

        <div v-if="showPromoForm && !cart.promo_code" class="space-y-3">
          <div class="flex space-x-2">
            <input 
              v-model="promoCode"
              type="text" 
              placeholder="Code promo"
              class="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
              @keyup.enter="applyPromoCode"
            >
            <button 
              @click="applyPromoCode"
              :disabled="!promoCode.trim() || isApplyingPromo"
              class="px-4 py-2 bg-brand-burgundy text-white rounded-md hover:bg-opacity-90 disabled:opacity-50"
            >
              {{ isApplyingPromo ? 'Application...' : 'Appliquer' }}
            </button>
          </div>
          <button 
            @click="showPromoForm = false"
            class="text-sm text-gray-600 hover:text-gray-800"
          >
            Annuler
          </button>
        </div>

        <div v-if="cart.promo_code" class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="font-medium text-green-600">{{ cart.promo_code }}</span>
            <span class="text-sm text-gray-600">appliqué</span>
          </div>
          <button 
            @click="removePromoCode"
            class="text-red-600 hover:text-red-800 text-sm"
          >
            Retirer
          </button>
        </div>
      </div>

      <!-- Order Totals -->
      <div class="space-y-3 border-t pt-4">
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Sous-total ({{ totalItems }} article{{ totalItems > 1 ? 's' : '' }})</span>
          <span class="font-medium">{{ formatPrice(cart.subtotal) }}</span>
        </div>

        <div v-if="cart.discount_amount > 0" class="flex justify-between text-sm">
          <span class="text-green-600">Remise</span>
          <span class="font-medium text-green-600">-{{ formatPrice(cart.discount_amount) }}</span>
        </div>

        <div v-if="deliveryMethod" class="flex justify-between text-sm">
          <span class="text-gray-600">{{ deliveryMethod.name }}</span>
          <span class="font-medium">
            {{ deliveryMethod.price > 0 ? formatPrice(deliveryMethod.price) : 'Gratuit' }}
          </span>
        </div>

        <div v-if="cart.tax_amount > 0" class="flex justify-between text-sm">
          <span class="text-gray-600">TVA</span>
          <span class="font-medium">{{ formatPrice(cart.tax_amount) }}</span>
        </div>

        <div class="flex justify-between text-lg font-semibold border-t pt-3">
          <span>Total</span>
          <span>{{ formatPrice(finalTotal) }}</span>
        </div>

        <!-- Loyalty Points -->
        <div v-if="cart.loyalty_points_earned > 0" class="text-sm text-center text-green-600 bg-green-50 p-2 rounded">
          <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
          Vous gagnerez {{ cart.loyalty_points_earned }} points de fidélité
        </div>
      </div>

      <!-- Estimated Delivery -->
      <div v-if="deliveryMethod && deliveryMethod.estimated_delivery" class="mt-6 p-4 bg-blue-50 rounded-lg">
        <div class="flex items-center space-x-2">
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="font-medium text-blue-900">Livraison estimée</p>
            <p class="text-sm text-blue-700">{{ formatDate(deliveryMethod.estimated_delivery) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useCartStore } from '@/stores/cart';
import { apiClient } from '@/services/api';

const props = defineProps({
  deliveryMethod: {
    type: Object,
    default: null
  }
});

const cartStore = useCartStore();

// State
const showPromoForm = ref(false);
const promoCode = ref('');
const isApplyingPromo = ref(false);

// Computed
const cart = computed(() => cartStore.cart);
const isLoading = computed(() => cartStore.isLoading);

const totalItems = computed(() => {
  if (!cart.value || !cart.value.items) return 0;
  return cart.value.items.reduce((total, item) => total + item.quantity, 0);
});

const finalTotal = computed(() => {
  let total = cart.value?.total || 0;
  if (props.deliveryMethod && props.deliveryMethod.price) {
    total += props.deliveryMethod.price;
  }
  return total;
});

// Methods
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

function calculateDiscount(item) {
  if (item.unit_price === item.discounted_price) return 0;
  return Math.round(((item.unit_price - item.discounted_price) / item.unit_price) * 100);
}

async function applyPromoCode() {
  if (!promoCode.value.trim()) return;
  
  isApplyingPromo.value = true;
  try {
    await apiClient.post('/cart/promo-code', {
      code: promoCode.value.trim()
    });
    
    // Refresh cart to get updated totals
    await cartStore.fetchCart();
    
    showPromoForm.value = false;
    promoCode.value = '';
  } catch (error) {
    console.error('Failed to apply promo code:', error);
    // Error notification will be shown by API interceptor
  } finally {
    isApplyingPromo.value = false;
  }
}

async function removePromoCode() {
  try {
    await apiClient.delete('/cart/promo-code');
    await cartStore.fetchCart();
  } catch (error) {
    console.error('Failed to remove promo code:', error);
  }
}

// Lifecycle
onMounted(() => {
  if (!cart.value) {
    cartStore.fetchCart();
  }
});

// Watch for delivery method changes to update total
watch(() => props.deliveryMethod, () => {
  // The computed finalTotal will automatically update
}, { deep: true });

// Expose data for parent component
defineExpose({
  cart: computed(() => cart.value),
  finalTotal,
  totalItems,
  isLoading
});
</script>