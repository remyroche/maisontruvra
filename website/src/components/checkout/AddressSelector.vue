<template>
  <div>
    <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>

    <div v-if="addresses.length > 0" class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div
        v-for="address in addresses"
        :key="address.id"
        @click="selectAddress(address)"
        :class="[
          'relative block cursor-pointer rounded-lg border bg-white px-6 py-4 shadow-sm focus:outline-none sm:flex sm:justify-between',
          { 'border-primary ring-2 ring-primary': selectedAddressId === address.id, 'border-gray-300': selectedAddressId !== address.id }
        ]"
      >
        <div class="flex items-center">
          <div class="text-sm">
            <p class="font-medium text-gray-900">{{ address.first_name }} {{ address.last_name }}</p>
            <div class="text-gray-500">
              <p>{{ address.street_line_1 }}</p>
              <p v-if="address.street_line_2">{{ address.street_line_2 }}</p>
              <p>{{ address.city }}, {{ address.postal_code }}</p>
              <p>{{ address.country }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6">
      <button @click="showNewAddressForm = !showNewAddressForm" type="button" class="text-sm font-medium text-primary hover:text-primary-dark">
        {{ showNewAddressForm ? $t('forms.cancel') : $t('address.addNew') }}
      </button>
    </div>

    <!-- New Address Form with Validation -->
    <div v-if="showNewAddressForm" class="mt-6">
      <VeeForm :validation-schema="addressSchema" @submit="onAddNewAddress" v-slot="{ isSubmitting }">
        <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
          <div>
            <label for="first-name" class="block text-sm font-medium text-gray-700">{{ $t('forms.firstName') }}</label>
            <VeeField type="text" name="first_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="first_name" class="text-sm text-red-600 mt-1" />
          </div>
          <div>
            <label for="last-name" class="block text-sm font-medium text-gray-700">{{ $t('forms.lastName') }}</label>
            <VeeField type="text" name="last_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="last_name" class="text-sm text-red-600 mt-1" />
          </div>
          <div class="sm:col-span-2">
            <label for="street-line-1" class="block text-sm font-medium text-gray-700">{{ $t('forms.address') }}</label>
            <VeeField type="text" name="street_line_1" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="street_line_1" class="text-sm text-red-600 mt-1" />
          </div>
          <div>
            <label for="city" class="block text-sm font-medium text-gray-700">{{ $t('forms.city') }}</label>
            <VeeField type="text" name="city" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="city" class="text-sm text-red-600 mt-1" />
          </div>
          <div>
            <label for="postal-code" class="block text-sm font-medium text-gray-700">{{ $t('forms.postalCode') }}</label>
            <VeeField type="text" name="postal_code" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="postal_code" class="text-sm text-red-600 mt-1" />
          </div>
          <div class="sm:col-span-2">
            <label for="country" class="block text-sm font-medium text-gray-700">{{ $t('forms.country') }}</label>
            <VeeField as="select" name="country" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm">
              <option value="" disabled>{{ $t('forms.selectCountry', { default: 'Select a country...' }) }}</option>
              <option v-for="country in availableCountries" :key="country.code" :value="country.name">
                {{ country.name }}
              </option>
            </VeeField>
            <VeeErrorMessage name="country" class="text-sm text-red-600 mt-1" />
          </div>
        </div>
        <div class="mt-6">
            <button
                type="submit"
                :disabled="isSubmitting"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400"
            >
                {{ $t('address.save') }}
            </button>
        </div>
      </VeeForm>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import * as yup from 'yup';
import api from '@/services/api';

const { t } = useI18n();

defineProps({
  title: { type: String, required: true },
  addresses: { type: Array, default: () => [] },
  selectedAddressId: { type: [String, Number], default: null },
});

const emit = defineEmits(['select-address', 'add-address']);

const showNewAddressForm = ref(false);
const availableCountries = ref([]);

onMounted(async () => {
  try {
    const response = await api.getDeliveryCountries();
    availableCountries.value = response.data;
  } catch (error) {
    console.error("Failed to fetch delivery countries:", error);
  }
});

const addressSchema = yup.object({
  first_name: yup.string().required(t('validation.required')),
  last_name: yup.string().required(t('validation.required')),
  street_line_1: yup.string().required(t('validation.required')),
  street_line_2: yup.string(),
  city: yup.string().required(t('validation.required')),
  postal_code: yup.string().required(t('validation.required')),
  country: yup.string().required(t('validation.required')),
});

const selectAddress = (address) => {
  emit('select-address', address);
};

const onAddNewAddress = (values, { resetForm }) => {
  emit('add-address', values);
  resetForm();
  showNewAddressForm.value = false;
};
</script>