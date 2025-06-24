<template>
  <div>
    <h2 class="text-lg font-medium text-gray-900">Méthode de livraison</h2>

    <RadioGroup v-model="checkoutStore.deliveryMethod" class="mt-4">
      <RadioGroupLabel class="sr-only"> Choisir une méthode de livraison </RadioGroupLabel>
      <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
        <RadioGroupOption as="template" v-for="method in deliveryMethods" :key="method.id" :value="method" v-slot="{ checked, active }">
          <div :class="[checked ? 'border-indigo-600' : 'border-gray-300', active ? 'border-indigo-600 ring-2 ring-indigo-600' : '', 'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none']">
            <span class="flex flex-1">
              <span class="flex flex-col">
                <RadioGroupLabel as="span" class="block text-sm font-medium text-gray-900">{{ method.title }}</RadioGroupLabel>
                <RadioGroupDescription as="span" class="mt-1 flex items-center text-sm text-gray-500">{{ method.turnaround }}</RadioGroupDescription>
                <RadioGroupDescription as="span" class="mt-6 text-sm font-medium text-gray-900">{{ method.price }}</RadioGroupDescription>
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
import { ref } from 'vue';
import { useCheckoutStore } from '../../js/stores/checkout';
import { RadioGroup, RadioGroupLabel, RadioGroupDescription, RadioGroupOption } from '@headlessui/vue';

const checkoutStore = useCheckoutStore();
const deliveryMethods = ref([
  { id: 1, title: 'Standard', turnaround: '4-10 jours ouvrés', price: '5,00 €' },
  { id: 2, title: 'Express', turnaround: '2-5 jours ouvrés', price: '16,00 €' },
]);

// Set default delivery method
if (!checkoutStore.deliveryMethod) {
    checkoutStore.deliveryMethod = deliveryMethods.value[0];
}
</script>
