<template>
  <div>
    <!-- Personal Addresses Section -->
    <div class="bg-white p-6 rounded-lg shadow">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg font-medium leading-6 text-gray-900">My Personal Addresses</h3>
          <p class="mt-1 text-sm text-gray-500">Manage your shipping addresses. You can add up to 3.</p>
        </div>
        <button 
          @click="openAddressModal(false)" 
          :disabled="personalAddresses.length >= 3"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark disabled:bg-gray-400 disabled:cursor-not-allowed">
          Add New Personal Address
        </button>
      </div>

      <div v-if="userStore.isLoading && !personalAddresses.length" class="mt-6 text-center text-gray-500">Loading addresses...</div>
      <div v-else-if="personalAddresses.length" class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div v-for="address in personalAddresses" :key="address.id" class="border rounded-lg p-4 flex flex-col justify-between">
          <address class="text-sm not-italic text-gray-600">
            {{ address.address_line_1 }}<br>
            <span v-if="address.address_line_2">{{ address.address_line_2 }}<br></span>
            {{ address.city }}, {{ address.state_province_region }} {{ address.postal_code }}<br>
            {{ address.country }}
          </address>
          <div class="mt-4 flex items-center justify-end space-x-3">
            <button @click="openAddressModal(false, address)" class="text-sm font-medium text-primary hover:text-primary-dark">Edit</button>
            <button @click="handleDeleteAddress(address.id)" class="text-sm font-medium text-red-600 hover:text-red-800">Delete</button>
          </div>
        </div>
      </div>
      <p v-else class="mt-6 text-sm text-gray-500">No personal addresses have been added yet.</p>
    </div>

    <!-- Invoice Address Section -->
    <div class="mt-8 bg-white p-6 rounded-lg shadow">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg font-medium leading-6 text-gray-900">My Invoice Address</h3>
          <p class="mt-1 text-sm text-gray-500">Your single address for all billing purposes.</p>
        </div>
        <button 
          v-if="!invoiceAddress"
          @click="openAddressModal(true)" 
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark">
          Add Invoice Address
        </button>
      </div>

      <div v-if="invoiceAddress" class="mt-6 border rounded-lg p-4 flex justify-between items-start">
         <address class="text-sm not-italic text-gray-600">
            {{ invoiceAddress.address_line_1 }}<br>
            <span v-if="invoiceAddress.address_line_2">{{ invoiceAddress.address_line_2 }}<br></span>
            {{ invoiceAddress.city }}, {{ invoiceAddress.state_province_region }} {{ invoiceAddress.postal_code }}<br>
            {{ invoiceAddress.country }}
          </address>
          <div class="flex items-center space-x-3">
            <button @click="openAddressModal(true, invoiceAddress)" class="text-sm font-medium text-primary hover:text-primary-dark">Edit</button>
            <button @click="handleDeleteAddress(invoiceAddress.id)" class="text-sm font-medium text-red-600 hover:text-red-800">Delete</button>
          </div>
      </div>
      <p v-else class="mt-6 text-sm text-gray-500">No invoice address has been set.</p>
    </div>

    <!-- Add/Edit Address Modal -->
    <div v-if="showAddressModal" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center p-4">
      <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h3 class="text-lg font-bold mb-4">{{ modalTitle }}</h3>
        <AddressForm :initial-data="editableAddress" @submit="handleAddressSubmit" @cancel="closeAddressModal" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from '@/stores/user';
import { storeToRefs } from 'pinia';
import AddressForm from '@/components/forms/AddressForm.vue';

const userStore = useUserStore();
const { personalAddresses, invoiceAddress } = storeToRefs(userStore);

const showAddressModal = ref(false);
const isEditing = ref(false);
const isBilling = ref(false);
const editableAddress = ref(null);

onMounted(() => {
  userStore.fetchAddresses();
});

const modalTitle = computed(() => {
    if (isEditing.value) {
        return isBilling.value ? 'Edit Invoice Address' : 'Edit Personal Address';
    }
    return isBilling.value ? 'Add Invoice Address' : 'Add New Personal Address';
});

const openAddressModal = (isBillingAddress, address = null) => {
  isBilling.value = isBillingAddress;
  if (address) {
    isEditing.value = true;
    editableAddress.value = { ...address };
  } else {
    isEditing.value = false;
    editableAddress.value = null;
  }
  showAddressModal.value = true;
};

const closeAddressModal = () => {
  showAddressModal.value = false;
  editableAddress.value = null;
};

const handleAddressSubmit = async (addressData) => {
  const payload = { ...addressData, is_billing_address: isBilling.value };
  if (isEditing.value) {
    await userStore.updateAddress(editableAddress.value.id, payload);
  } else {
    await userStore.addAddress(payload);
  }
  closeAddressModal();
};

const handleDeleteAddress = async (addressId) => {
  if (confirm('Are you sure you want to delete this address?')) {
    await userStore.deleteAddress(addressId);
  }
};
</script>
