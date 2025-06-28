<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Success Header -->
      <div class="text-center mb-8">
        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
          <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900">Commande confirmée !</h1>
        <p class="mt-2 text-lg text-gray-600">
          Merci pour votre commande. Nous préparons vos truffes d'exception avec le plus grand soin.
        </p>
      </div>

      <!-- Order Details -->
      <div v-if="order" class="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Détails de votre commande</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Numéro de commande</h3>
            <p class="text-lg font-mono text-brand-burgundy">#{{ order.order_number }}</p>
          </div>
          
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Date de commande</h3>
            <p class="text-gray-600">{{ formatDate(order.created_at) }}</p>
          </div>
          
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Total</h3>
            <p class="text-lg font-semibold">{{ formatPrice(order.total_amount) }}</p>
          </div>
          
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Statut</h3>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              {{ order.status }}
            </span>
          </div>
        </div>

        <!-- Delivery Information -->
        <div class="border-t pt-6">
          <h3 class="font-medium text-gray-900 mb-4">Informations de livraison</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 class="text-sm font-medium text-gray-700 mb-1">Adresse de livraison</h4>
              <div class="text-sm text-gray-600">
                <p>{{ order.shipping_address.first_name }} {{ order.shipping_address.last_name }}</p>
                <p>{{ order.shipping_address.street_address }}</p>
                <p v-if="order.shipping_address.apartment">{{ order.shipping_address.apartment }}</p>
                <p>{{ order.shipping_address.postal_code }} {{ order.shipping_address.city }}</p>
                <p v-if="order.shipping_address.country">{{ order.shipping_address.country }}</p>
              </div>
            </div>
            
            <div>
              <h4 class="text-sm font-medium text-gray-700 mb-1">Mode de livraison</h4>
              <p class="text-sm text-gray-600">{{ order.delivery_method.name }}</p>
              <p v-if="order.estimated_delivery" class="text-sm text-gray-600 mt-1">
                Livraison estimée : {{ formatDate(order.estimated_delivery) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Items -->
      <div v-if="order && order.items" class="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Articles commandés</h2>
        
        <div class="space-y-4">
          <div 
            v-for="item in order.items" 
            :key="item.id"
            class="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg"
          >
            <img 
              :src="item.product.image_url || '/placeholder-product.jpg'" 
              :alt="item.product.name"
              class="w-16 h-16 object-cover rounded-md"
            >
            
            <div class="flex-1">
              <h3 class="font-medium text-gray-900">{{ item.product.name }}</h3>
              <p v-if="item.product.variant" class="text-sm text-gray-600">{{ item.product.variant }}</p>
              <p v-if="item.product.weight" class="text-sm text-gray-600">{{ item.product.weight }}</p>
              
              <div class="flex items-center justify-between mt-2">
                <span class="text-sm text-gray-600">Quantité: {{ item.quantity }}</span>
                <span class="font-medium">{{ formatPrice(item.total_price) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Next Steps -->
      <div class="bg-blue-50 rounded-lg p-6 mb-6">
        <h2 class="text-lg font-semibold text-blue-900 mb-4">Prochaines étapes</h2>
        <div class="space-y-3 text-sm text-blue-800">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <div>
              <p class="font-medium">Confirmation par email</p>
              <p>Vous recevrez un email de confirmation avec tous les détails de votre commande.</p>
            </div>
          </div>
          
          <div class="flex items-start">
            <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <div>
              <p class="font-medium">Préparation de votre commande</p>
              <p>Nos experts sélectionnent et préparent vos truffes avec le plus grand soin.</p>
            </div>
          </div>
          
          <div class="flex items-start">
            <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2-2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <div>
              <p class="font-medium">Expédition et suivi</p>
              <p>Vous recevrez un numéro de suivi dès l'expédition de votre commande.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Besoin d'aide ?</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Service client</h3>
            <p class="text-sm text-gray-600 mb-2">
              Notre équipe est à votre disposition pour toute question concernant votre commande.
            </p>
            <div class="space-y-1 text-sm">
              <p class="text-gray-600">📧 contact@maisontruvra.com</p>
              <p class="text-gray-600">📞 01 23 45 67 89</p>
              <p class="text-gray-600">🕒 Lundi - Vendredi : 9h - 18h</p>
            </div>
          </div>
          
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Suivi de commande</h3>
            <p class="text-sm text-gray-600 mb-3">
              Suivez l'état de votre commande en temps réel depuis votre espace client.
            </p>
            <router-link 
              v-if="userStore.isLoggedIn"
              to="/account/orders"
              class="inline-flex items-center px-4 py-2 border border-brand-burgundy text-brand-burgundy rounded-md hover:bg-brand-burgundy hover:text-white transition-colors"
            >
              Voir mes commandes
            </router-link>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link 
          to="/shop"
          class="inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
        >
          Continuer mes achats
        </router-link>
        
        <router-link 
          to="/"
          class="inline-flex items-center justify-center px-6 py-3 bg-brand-burgundy text-white rounded-md hover:bg-opacity-90 transition-colors"
        >
          Retour à l'accueil
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { apiClient } from '@/services/api';

const route = useRoute();
const userStore = useUserStore();

// State
const order = ref(null);
const isLoading = ref(false);
const error = ref(null);

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
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

async function fetchOrder() {
  const orderId = route.params.id || route.query.order_id;
  if (!orderId) {
    error.value = 'Numéro de commande manquant';
    return;
  }

  isLoading.value = true;
  try {
    const response = await apiClient.get(`/orders/${orderId}`);
    order.value = response.order;
  } catch (err) {
    console.error('Failed to fetch order:', err);
    error.value = 'Impossible de charger les détails de la commande';
  } finally {
    isLoading.value = false;
  }
}

// Lifecycle
onMounted(() => {
  fetchOrder();
});
</script>