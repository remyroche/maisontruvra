<template>
  <div>
    <h2 class="text-lg font-medium text-gray-900">Adresse de livraison</h2>

    <div v-if="userStore.addresses.length > 0" class="mt-4">
      <RadioGroup v-model="selectedAddress">
        <RadioGroupLabel class="sr-only"> Choisir une adresse de livraison </RadioGroupLabel>
        <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
          <RadioGroupOption as="template" v-for="address in userStore.addresses" :key="address.id" :value="address" v-slot="{ checked, active }">
            <div :class="[checked ? 'border-indigo-600' : 'border-gray-300', active ? 'border-indigo-600 ring-2 ring-indigo-600' : '', 'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none']">
              <span class="flex flex-1">
                <span class="flex flex-col">
                  <RadioGroupLabel as="span" class="block text-sm font-medium text-gray-900">{{ address.street }}</RadioGroupLabel>
                  <RadioGroupDescription as="span" class="mt-1 flex items-center text-sm text-gray-500">{{ address.city }}, {{ address.postal_code }}</RadioGroupDescription>
                  <RadioGroupDescription as="span" class="mt-1 flex items-center text-sm text-gray-500">{{ address.country }}</RadioGroupDescription>
                </span>
              </span>
              <span v-if="checked" class="pointer-events-none absolute -right-px -top-px h-full w-5" aria-hidden="true">
                <svg class="h-full w-full text-indigo-600" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>
              </span>
            </div>
          </RadioGroupOption>
        </div>
      </RadioGroup>
      <button @click="showAddAddressForm = true" class="mt-4 text-sm font-medium text-indigo-600 hover:text-indigo-500">Ajouter une nouvelle adresse</button>
    </div>
    
    <div v-if="showAddAddressForm || userStore.addresses.length === 0" class="mt-4">
        <!-- A form to add a new address would go here -->
        <p class="text-sm text-gray-500">Formulaire d'ajout d'adresse à implémenter.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../js/stores/user';
import { RadioGroup, RadioGroupLabel, RadioGroupDescription, RadioGroupOption } from '@headlessui/vue';

const userStore = useUserStore();
const selectedAddress = ref(null);
const showAddAddressForm = ref(false);

onMounted(async () => {
    if (userStore.addresses.length === 0) {
        await userStore.fetchAddresses();
    }
    if (userStore.addresses.length > 0) {
        selectedAddress.value = userStore.addresses[0];
    }
});
</script>
