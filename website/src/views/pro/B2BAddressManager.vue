<template>
  <div class="bg-white p-6 rounded-lg shadow">
    <div class="flex justify-between items-center">
      <div>
        <h3 class="text-lg font-medium leading-6 text-gray-900">Company Addresses</h3>
        <p class="mt-1 text-sm text-gray-500">Manage shared billing and shipping addresses for your company.</p>
      </div>
      <button @click="openAddressModal()" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark">
        Add New Address
      </button>
    </div>

    <!-- Address List -->
    <div v-if="store.isLoading" class="mt-6 text-center">Loading addresses...</div>
    <div v-else-if="store.addresses.length" class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
      <div v-for="address in store.addresses" :key="address.id" class="border rounded-lg p-4 flex flex-col justify-between">
        <address class="text-sm not-italic text-gray-600">
          {{ address.address_line_1 }}<br>
          <span v-if="address.address_line_2">{{ address.address_line_2 }}<br></span>
          {{ address.city }}, {{ address.state_province_region }} {{ address.postal_code }}<br>
          {{ address.country }}
        </address>
        <div class="mt-4 flex items-center justify-end space-x-3">
          <button @click="openAddressModal(address)" class="text-sm font-medium text-primary hover:text-primary-dark">Edit</button>
          <button @click="handleDeleteAddress(address.id)" class="text-sm font-medium text-red-600 hover:text-red-800">Delete</button>
        </div>
      </div>
    </div>
    <p v-else class="mt-6 text-sm text-gray-500">No company addresses have been added yet.</p>

    <!-- Add/Edit Address Modal -->
    <div v-if="showAddressModal" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center p-4">
      <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-lg">
        <h3 class="text-lg font-bold mb-4">{{ isEditing ? 'Edit Address' : 'Add New Address' }}</h3>
        <AddressForm :initial-data="editableAddress" @submit="handleAddressSubmit" @cancel="closeAddressModal" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useB2BStore } from '@/stores/b2b';
import AddressForm from '@/components/forms/AddressForm.vue';

const store = useB2BStore();
const showAddressModal = ref(false);
const isEditing = ref(false);
const editableAddress = ref(null);

onMounted(() => {
  store.fetchB2BAddresses();
});

const openAddressModal = (address = null) => {
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
  if (isEditing.value) {
    await store.updateB2BAddress(editableAddress.value.id, addressData);
  } else {
    await store.addB2BAddress(addressData);
  }
  closeAddressModal();
};

const handleDeleteAddress = async (addressId) => {
  if (confirm('Are you sure you want to delete this address?')) {
    await store.deleteB2BAddress(addressId);
  }
};
</script>
