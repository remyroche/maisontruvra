<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Finaliser ma commande</h1>
        <p class="mt-2 text-gray-600">Quelques étapes simples pour recevoir vos truffes d'exception</p>
      </div>

      <!-- Progress Steps -->
      <div class="mb-8">
        <nav aria-label="Progress">
          <ol class="flex items-center justify-center space-x-4 md:space-x-8">
            <li class="flex items-center">
              <div class="flex items-center">
                <div 
                  class="flex items-center justify-center w-8 h-8 rounded-full border-2 text-sm font-medium"
                  :class="getStepClasses('contact')"
                >
                  <svg v-if="checkoutStore.isContactComplete" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span v-else>1</span>
                </div>
                <span class="ml-2 text-sm font-medium" :class="getStepTextClasses('contact')">
                  Contact
                </span>
              </div>
            </li>

            <li class="flex items-center">
              <svg class="w-5 h-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
              <div class="flex items-center ml-4">
                <div 
                  class="flex items-center justify-center w-8 h-8 rounded-full border-2 text-sm font-medium"
                  :class="getStepClasses('shipping')"
                >
                  <svg v-if="checkoutStore.isShippingComplete" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span v-else>2</span>
                </div>
                <span class="ml-2 text-sm font-medium" :class="getStepTextClasses('shipping')">
                  Livraison
                </span>
              </div>
            </li>

            <li class="flex items-center">
              <svg class="w-5 h-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
              <div class="flex items-center ml-4">
                <div 
                  class="flex items-center justify-center w-8 h-8 rounded-full border-2 text-sm font-medium"
                  :class="getStepClasses('delivery')"
                >
                  <svg v-if="checkoutStore.isDeliveryComplete" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span v-else>3</span>
                </div>
                <span class="ml-2 text-sm font-medium" :class="getStepTextClasses('delivery')">
                  Mode de livraison
                </span>
              </div>
            </li>

            <li class="flex items-center">
              <svg class="w-5 h-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
              <div class="flex items-center ml-4">
                <div 
                  class="flex items-center justify-center w-8 h-8 rounded-full border-2 text-sm font-medium"
                  :class="getStepClasses('payment')"
                >
                  <span>4</span>
                </div>
                <span class="ml-2 text-sm font-medium" :class="getStepTextClasses('payment')">
                  Paiement
                </span>
              </div>
            </li>
          </ol>
        </nav>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column - Forms -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Contact Section -->
          <div v-if="checkoutStore.activeSection === 'contact'">
            <LoginForm 
              v-if="!checkoutStore.isGuestMode && !userStore.isLoggedIn"
              @login-success="handleLoginSuccess"
              @switch-to-guest="handleSwitchToGuest"
            />
            <GuestCheckoutForm 
              v-else-if="checkoutStore.isGuestMode"
              @guest-info-submitted="handleGuestInfoSubmitted"
              @switch-to-login="handleSwitchToLogin"
            />
            <div v-else class="bg-white rounded-lg shadow-sm border p-6">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">Connecté en tant que</h3>
                  <p class="text-gray-600">{{ userStore.profile?.email }}</p>
                </div>
                <button 
                  @click="proceedToShipping"
                  class="bg-brand-burgundy text-white px-6 py-2 rounded-md hover:bg-opacity-90"
                >
                  Continuer
                </button>
              </div>
            </div>
          </div>

          <!-- Shipping Section -->
          <div v-if="checkoutStore.activeSection === 'shipping'">
            <AddressSelector 
              ref="addressSelector"
              @address-selected="handleAddressSelected"
            />
            <div v-if="selectedAddress" class="mt-6 flex justify-between">
              <button 
                @click="checkoutStore.setActiveSection('contact')"
                class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Retour
              </button>
              <button 
                @click="proceedToDelivery"
                class="bg-brand-burgundy text-white px-6 py-2 rounded-md hover:bg-opacity-90"
              >
                Continuer vers la livraison
              </button>
            </div>
          </div>

          <!-- Delivery Section -->
          <div v-if="checkoutStore.activeSection === 'delivery'">
            <DeliveryMethodSelector 
              ref="deliverySelector"
              :shipping-address="checkoutStore.shippingAddress"
              :cart-total="orderSummary?.finalTotal || 0"
              @method-selected="handleDeliveryMethodSelected"
            />
            <div v-if="selectedDeliveryMethod" class="mt-6 flex justify-between">
              <button 
                @click="checkoutStore.setActiveSection('shipping')"
                class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Retour
              </button>
              <button 
                @click="proceedToPayment"
                class="bg-brand-burgundy text-white px-6 py-2 rounded-md hover:bg-opacity-90"
              >
                Continuer vers le paiement
              </button>
            </div>
          </div>

          <!-- Payment Section -->
          <div v-if="checkoutStore.activeSection === 'payment'" class="bg-white rounded-lg shadow-sm border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Paiement</h3>
            
            <!-- Order Review -->
            <div class="mb-6 p-4 bg-gray-50 rounded-lg">
              <h4 class="font-medium text-gray-900 mb-3">Récapitulatif de votre commande</h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span>Contact:</span>
                  <span>{{ checkoutStore.guestEmail || userStore.profile?.email }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Livraison:</span>
                  <span>{{ formatAddress(checkoutStore.shippingAddress) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Mode de livraison:</span>
                  <span>{{ checkoutStore.deliveryMethod?.name }}</span>
                </div>
              </div>
            </div>

            <!-- Payment Methods -->
            <div class="space-y-4 mb-6">
              <h4 class="font-medium text-gray-900">Mode de paiement</h4>
              
              <!-- Credit Card -->
              <div class="border rounded-lg p-4">
                <div class="flex items-center mb-3">
                  <input 
                    id="card"
                    type="radio" 
                    name="payment"
                    value="card"
                    checked
                    class="text-brand-burgundy focus:ring-brand-burgundy"
                  >
                  <label for="card" class="ml-2 font-medium">Carte bancaire</label>
                  <div class="ml-auto flex space-x-2">
                    <img src="/images/visa.svg" alt="Visa" class="h-6">
                    <img src="/images/mastercard.svg" alt="Mastercard" class="h-6">
                  </div>
                </div>
                <p class="text-sm text-gray-600">Paiement sécurisé par Stripe</p>
              </div>

              <!-- PayPal -->
              <div class="border rounded-lg p-4 opacity-50">
                <div class="flex items-center">
                  <input 
                    id="paypal"
                    type="radio" 
                    name="payment"
                    value="paypal"
                    disabled
                    class="text-brand-burgundy focus:ring-brand-burgundy"
                  >
                  <label for="paypal" class="ml-2 font-medium text-gray-500">PayPal</label>
                  <span class="ml-auto text-sm text-gray-500">Bientôt disponible</span>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-between">
              <button 
                @click="checkoutStore.setActiveSection('delivery')"
                class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Retour
              </button>
              <button 
                @click="handleSubmitOrder"
                :disabled="checkoutStore.isSubmitting"
                class="bg-brand-burgundy text-white px-8 py-3 rounded-md font-medium hover:bg-opacity-90 disabled:opacity-50"
              >
                {{ checkoutStore.isSubmitting ? 'Traitement...' : 'Finaliser la commande' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Right Column - Order Summary -->
        <div class="lg:col-span-1">
          <div class="sticky top-8">
            <OrderSummary 
              ref="orderSummary"
              :delivery-method="checkoutStore.deliveryMethod"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCheckoutStore } from '@/stores/checkout';
import { useUserStore } from '@/stores/user';
import { useCartStore } from '@/stores/cart';
import AddressSelector from '@/components/checkout/AddressSelector.vue';
import DeliveryMethodSelector from '@/components/checkout/DeliveryMethodSelector.vue';
import OrderSummary from '@/components/checkout/OrderSummary.vue';
import GuestCheckoutForm from '@/components/checkout/GuestCheckoutForm.vue';
import LoginForm from '@/components/checkout/LoginForm.vue';

const router = useRouter();
const checkoutStore = useCheckoutStore();
const userStore = useUserStore();
const cartStore = useCartStore();

// Component refs
const addressSelector = ref(null);
const deliverySelector = ref(null);
const orderSummary = ref(null);

// Local state
const selectedAddress = ref(null);
const selectedDeliveryMethod = ref(null);

// Computed
const isLoggedIn = computed(() => userStore.isLoggedIn);

// Step styling methods
function getStepClasses(step) {
  const isActive = checkoutStore.activeSection === step;
  const isComplete = getStepComplete(step);
  
  if (isComplete) {
    return 'bg-brand-burgundy border-brand-burgundy text-white';
  } else if (isActive) {
    return 'bg-white border-brand-burgundy text-brand-burgundy';
  } else {
    return 'bg-white border-gray-300 text-gray-500';
  }
}

function getStepTextClasses(step) {
  const isActive = checkoutStore.activeSection === step;
  const isComplete = getStepComplete(step);
  
  if (isComplete || isActive) {
    return 'text-brand-burgundy';
  } else {
    return 'text-gray-500';
  }
}

function getStepComplete(step) {
  switch (step) {
    case 'contact':
      return checkoutStore.isContactComplete;
    case 'shipping':
      return checkoutStore.isShippingComplete;
    case 'delivery':
      return checkoutStore.isDeliveryComplete;
    default:
      return false;
  }
}

// Event handlers
function handleLoginSuccess(user) {
  checkoutStore.setGuestMode(false);
  proceedToShipping();
}

function handleSwitchToGuest() {
  checkoutStore.setGuestMode(true);
}

function handleSwitchToLogin() {
  checkoutStore.setGuestMode(false);
}

function handleGuestInfoSubmitted(guestData) {
  checkoutStore.setGuestDetails(guestData);
}

function handleAddressSelected(address) {
  selectedAddress.value = address;
  checkoutStore.setShippingAddress(address);
}

function handleDeliveryMethodSelected(method) {
  selectedDeliveryMethod.value = method;
  checkoutStore.setDeliveryMethod(method);
}

// Navigation methods
function proceedToShipping() {
  if (isLoggedIn.value || checkoutStore.isGuestMode) {
    checkoutStore.setActiveSection('shipping');
  }
}

function proceedToDelivery() {
  if (selectedAddress.value) {
    checkoutStore.setActiveSection('delivery');
  }
}

function proceedToPayment() {
  if (selectedDeliveryMethod.value) {
    checkoutStore.setActiveSection('payment');
  }
}

async function handleSubmitOrder() {
  try {
    await checkoutStore.submitOrder();
    // The store will handle the redirect on success
  } catch (error) {
    console.error('Order submission failed:', error);
    // Error notification will be shown by the API interceptor
  }
}

// Utility methods
function formatAddress(address) {
  if (!address) return '';
  
  const parts = [
    address.street_address,
    address.city,
    address.postal_code
  ].filter(Boolean);
  
  return parts.join(', ');
}

// Lifecycle
onMounted(async () => {
  // Check authentication status
  if (userStore.isLoggedIn === null) {
    await userStore.checkAuthStatus();
  }
  
  // Ensure cart is loaded
  if (!cartStore.cart) {
    await cartStore.fetchCart();
  }
  
  // Check if cart is empty and redirect to shop
  if (!cartStore.cart || !cartStore.cart.items || cartStore.cart.items.length === 0) {
    router.push({ name: 'Shop' });
    return;
  }
  
  // Set initial state based on authentication
  if (userStore.isLoggedIn) {
    checkoutStore.setGuestMode(false);
    // If already logged in, mark contact as complete and proceed to shipping
    if (!checkoutStore.isContactComplete) {
      checkoutStore.setGuestDetails({ email: userStore.profile?.email });
    }
  } else {
    // Start with login form for non-authenticated users
    checkoutStore.setGuestMode(false);
    checkoutStore.setActiveSection('contact');
  }
});
</script>