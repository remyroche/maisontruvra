<template>
  <div>
    <h2 class="text-lg font-medium text-gray-900">Coordonnées</h2>

    <Form @submit="nextStep" class="mt-4">
      <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Adresse e-mail</label>
          <Field name="email" type="email" id="email" v-model="checkoutStore.guestDetails.email" rules="required|email" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
          <ErrorMessage name="email" class="text-sm text-red-600 mt-1" />
        </div>

        <div>
          <label for="phone" class="block text-sm font-medium text-gray-700">Téléphone (facultatif)</label>
          <Field name="phone" type="text" id="phone" v-model="checkoutStore.guestDetails.phone" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        </div>

        <div class="sm:col-span-2">
          <label for="address" class="block text-sm font-medium text-gray-700">Adresse</label>
          <Field name="address" type="text" id="address" v-model="checkoutStore.shippingAddress.street" rules="required" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
          <ErrorMessage name="address" class="text-sm text-red-600 mt-1" />
        </div>
        
        <div>
            <label for="city" class="block text-sm font-medium text-gray-700">Ville</label>
            <Field name="city" type="text" id="city" v-model="checkoutStore.shippingAddress.city" rules="required" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            <ErrorMessage name="city" class="text-sm text-red-600 mt-1" />
        </div>
        
        <div>
            <label for="postal_code" class="block text-sm font-medium text-gray-700">Code Postal</label>
            <Field name="postal_code" type="text" id="postal_code" v-model="checkoutStore.shippingAddress.postal_code" rules="required" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            <ErrorMessage name="postal_code" class="text-sm text-red-600 mt-1" />
        </div>
      </div>
    </Form>
  </div>
</template>

<script setup>
import { Form, Field, ErrorMessage } from 'vee-validate';
import { useCheckoutStore } from '../../js/stores/checkout';

const checkoutStore = useCheckoutStore();

function nextStep() {
    // This function can be used to advance the checkout flow,
    // though for this design, the main button handles it.
    console.log("Form submitted, advancing to next step...");
}
</script>
