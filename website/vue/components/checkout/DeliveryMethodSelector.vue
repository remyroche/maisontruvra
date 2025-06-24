<template>
  <div>
    <h2 class="text-lg font-medium text-gray-900">Méthode de livraison</h2>

    <div v-if="loading" class="mt-4 text-center text-gray-500">
      <p>Chargement des options de livraison...</p>
    </div>
    
    <div v-else-if="error" class="mt-4 text-center text-red-500">
      <p>{{ error }}</p>
    </div>

    <RadioGroup v-else v-model="checkoutStore.deliveryMethod" class="mt-4">
      <RadioGroupLabel class="sr-only"> Choisir une méthode de livraison </RadioGroupLabel>
      <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
        <RadioGroupOption as="template" v-for="method in deliveryMethods" :key="method.id" :value="method" v-slot="{ checked, active }">
          <div :class="[checked ? 'border-indigo-600' : 'border-gray-300', active ? 'border-indigo-600 ring-2 ring-indigo-600' : '', 'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none']">
            <span class="flex flex-1">
              <span class="flex flex-col">
                <RadioGroupLabel as="span" class="block text-sm font-medium text-gray-900">{{ method.title }}</RadioGroupLabel>
                <RadioGroupDescription as="span" class="mt-1 flex items-center text-sm text-gray-500">{{ method.turnaround }}</RadioGroupDescription>
                <RadioGroupDescription as="span" class="mt-6 text-sm font-medium text-gray-900">{{ method.displayPrice }}</RadioGroupDescription>
              </span>
            </span>
            <span v-if="checked" class="pointer-events-none absolute -right-px -top-px h-full w-5" aria-hidden="true">
              <svg class="h-full w-full text-indigo-600" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>
            </span>
          </div>
        </RadioGroupOption>
      </div>
    </RadioGroup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useCheckoutStore } from '../../js/stores/checkout';
import { RadioGroup, RadioGroupLabel, RadioGroupDescription, RadioGroupOption } from '@headlessui/vue';
import apiClient from '../../js/api-client';

const checkoutStore = useCheckoutStore();
const deliveryMethods = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    // This new apiClient method will fetch data from the backend
    const methods = await apiClient.getDeliveryMethods();
    deliveryMethods.value = methods.map(m => ({
        ...m,
        // Ensure price is a number and create a display string
        price: parseFloat(m.price),
        displayPrice: `${parseFloat(m.price).toFixed(2).replace('.', ',')} €`
    }));

    // Set default delivery method if not already set and methods are available
    if (!checkoutStore.deliveryMethod && deliveryMethods.value.length > 0) {
        checkoutStore.deliveryMethod = deliveryMethods.value[0];
    }
  } catch (err) {
    console.error("Failed to fetch delivery methods:", err);
    error.value = "Impossible de charger les méthodes de livraison.";
  } finally {
    loading.value = false;
  }
});
</script>
