<template>
  <div class="bg-white rounded-lg shadow-sm border p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Adresse de livraison</h3>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-burgundy"></div>
    </div>

    <!-- Address Selection -->
    <div v-else>
      <!-- Existing Addresses -->
      <div v-if="addresses.length > 0" class="space-y-3 mb-6">
        <div 
          v-for="address in addresses" 
          :key="address.id"
          class="border rounded-lg p-4 cursor-pointer transition-colors"
          :class="{
            'border-brand-burgundy bg-brand-cream': selectedAddress?.id === address.id,
            'border-gray-200 hover:border-gray-300': selectedAddress?.id !== address.id
          }"
          @click="selectAddress(address)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-2">
                <input 
                  type="radio" 
                  :checked="selectedAddress?.id === address.id"
                  class="text-brand-burgundy focus:ring-brand-burgundy"
                  readonly
                >
                <span class="ml-2 font-medium text-gray-900">{{ address.label || 'Adresse' }}</span>
                <span v-if="address.is_default" class="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                  Par défaut
                </span>
              </div>
              <div class="text-sm text-gray-600 ml-6">
                <p>{{ address.first_name }} {{ address.last_name }}</p>
                <p>{{ address.street_address }}</p>
                <p v-if="address.apartment">{{ address.apartment }}</p>
                <p>{{ address.postal_code }} {{ address.city }}</p>
                <p v-if="address.country">{{ address.country }}</p>
                <p v-if="address.phone">{{ address.phone }}</p>
              </div>
            </div>
            <button 
              @click.stop="editAddress(address)"
              class="text-gray-400 hover:text-gray-600 p-1"
              title="Modifier l'adresse"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Add New Address Button -->
      <button 
        @click="showAddressForm = true"
        class="w-full border-2 border-dashed border-gray-300 rounded-lg p-4 text-gray-600 hover:border-gray-400 hover:text-gray-700 transition-colors"
      >
        <svg class="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        Ajouter une nouvelle adresse
      </button>

      <!-- Address Form Modal -->
      <Modal v-if="showAddressForm" @close="closeAddressForm">
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ editingAddress ? 'Modifier l\'adresse' : 'Nouvelle adresse' }}
          </h3>
        </template>
        
        <form @submit.prevent="saveAddress" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Prénom *</label>
              <input 
                v-model="addressForm.first_name"
                type="text" 
                required
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
              <input 
                v-model="addressForm.last_name"
                type="text" 
                required
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Libellé de l'adresse</label>
            <input 
              v-model="addressForm.label"
              type="text" 
              placeholder="Domicile, Bureau, etc."
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Adresse *</label>
            <input 
              v-model="addressForm.street_address"
              type="text" 
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            >
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Complément d'adresse</label>
            <input 
              v-model="addressForm.apartment"
              type="text" 
              placeholder="Appartement, étage, etc."
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            >
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Code postal *</label>
              <input 
                v-model="addressForm.postal_code"
                type="text" 
                required
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ville *</label>
              <input 
                v-model="addressForm.city"
                type="text" 
                required
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Pays</label>
            <select 
              v-model="addressForm.country"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            >
              <option value="France">France</option>
              <option value="Belgique">Belgique</option>
              <option value="Suisse">Suisse</option>
              <option value="Luxembourg">Luxembourg</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
            <input 
              v-model="addressForm.phone"
              type="tel" 
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            >
          </div>

          <div class="flex items-center">
            <input 
              v-model="addressForm.is_default"
              type="checkbox" 
              id="is_default"
              class="text-brand-burgundy focus:ring-brand-burgundy"
            >
            <label for="is_default" class="ml-2 text-sm text-gray-700">
              Définir comme adresse par défaut
            </label>
          </div>

          <div class="flex justify-end space-x-3 pt-4">
            <button 
              type="button" 
              @click="closeAddressForm"
              class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Annuler
            </button>
            <button 
              type="submit" 
              :disabled="isSaving"
              class="px-4 py-2 bg-brand-burgundy text-white rounded-md hover:bg-opacity-90 disabled:opacity-50"
            >
              {{ isSaving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { apiClient } from '@/services/api';
import { useUserStore } from '@/stores/user';
import Modal from '@/components/ui/Modal.vue';

const emit = defineEmits(['address-selected']);

const userStore = useUserStore();

// State
const addresses = ref([]);
const selectedAddress = ref(null);
const isLoading = ref(false);
const showAddressForm = ref(false);
const editingAddress = ref(null);
const isSaving = ref(false);

// Form data
const addressForm = ref({
  first_name: '',
  last_name: '',
  label: '',
  street_address: '',
  apartment: '',
  postal_code: '',
  city: '',
  country: 'France',
  phone: '',
  is_default: false
});

// Computed
const hasAddresses = computed(() => addresses.value.length > 0);

// Methods
async function fetchAddresses() {
  if (!userStore.isLoggedIn) return;
  
  isLoading.value = true;
  try {
    const response = await apiClient.get('/user/addresses');
    addresses.value = response.addresses || [];
    
    // Auto-select default address if available
    const defaultAddress = addresses.value.find(addr => addr.is_default);
    if (defaultAddress && !selectedAddress.value) {
      selectAddress(defaultAddress);
    }
  } catch (error) {
    console.error('Failed to fetch addresses:', error);
  } finally {
    isLoading.value = false;
  }
}

function selectAddress(address) {
  selectedAddress.value = address;
  emit('address-selected', address);
}

function editAddress(address) {
  editingAddress.value = address;
  addressForm.value = { ...address };
  showAddressForm.value = true;
}

function closeAddressForm() {
  showAddressForm.value = false;
  editingAddress.value = null;
  resetForm();
}

function resetForm() {
  addressForm.value = {
    first_name: '',
    last_name: '',
    label: '',
    street_address: '',
    apartment: '',
    postal_code: '',
    city: '',
    country: 'France',
    phone: '',
    is_default: false
  };
}

async function saveAddress() {
  isSaving.value = true;
  try {
    let response;
    if (editingAddress.value) {
      // Update existing address
      response = await apiClient.put(`/user/addresses/${editingAddress.value.id}`, addressForm.value);
    } else {
      // Create new address
      response = await apiClient.post('/user/addresses', addressForm.value);
    }

    // Refresh addresses list
    await fetchAddresses();
    
    // Auto-select the new/updated address
    const savedAddress = response.address;
    if (savedAddress) {
      selectAddress(savedAddress);
    }
    
    closeAddressForm();
  } catch (error) {
    console.error('Failed to save address:', error);
  } finally {
    isSaving.value = false;
  }
}

// Lifecycle
onMounted(() => {
  fetchAddresses();
});

// Expose methods for parent component
defineExpose({
  selectedAddress: computed(() => selectedAddress.value),
  hasValidSelection: computed(() => !!selectedAddress.value)
});
</script>