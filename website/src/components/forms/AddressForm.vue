<template>
  <div class="space-y-4">
    <div>
      <label for="address" class="block text-sm font-medium text-gray-900">Adresse</label>
      <div class="mt-2">
        <input type="text" id="address" v-model="form.addressLine1" @input="emitUpdate"
               class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm"
               required autocomplete="street-address">
      </div>
    </div>
    <div>
      <label for="apartment" class="block text-sm font-medium text-gray-900">Appartement, suite, etc. (facultatif)</label>
      <div class="mt-2">
        <input type="text" id="apartment" v-model="form.addressLine2" @input="emitUpdate"
               class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm">
      </div>
    </div>
    <div class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-12">
      <div class="sm:col-span-6">
        <label for="city" class="block text-sm font-medium text-gray-900">Ville</label>
        <div class="mt-2">
          <input type="text" id="city" v-model="form.city" @input="emitUpdate"
                 class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm"
                 required autocomplete="address-level2">
        </div>
      </div>
      <div class="sm:col-span-6">
        <label for="postalCode" class="block text-sm font-medium text-gray-900">Code Postal</label>
        <div class="mt-2">
          <input type="text" id="postalCode" v-model="form.postalCode" @input="emitUpdate"
                 class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm"
                 required autocomplete="postal-code">
        </div>
      </div>
    </div>
     <div>
      <label for="country" class="block text-sm font-medium text-gray-900">Pays</label>
      <div class="mt-2">
        <input type="text" id="country" v-model="form.country" @input="emitUpdate"
               class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm"
               required autocomplete="country-name">
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({ addressLine1: '', addressLine2: '', city: '', postalCode: '', country: 'France' })
  }
});

const emit = defineEmits(['update:modelValue']);

const form = reactive({ ...props.modelValue });

watch(() => props.modelValue, (newValue) => {
  Object.assign(form, newValue);
}, { deep: true });

const emitUpdate = () => {
  emit('update:modelValue', { ...form });
};
</script>
