<template>
  <div>
    <h3 class="text-lg font-medium text-gray-900 mb-2">{{ $t('checkout.contactInfo') }}</h3>
    <p class="text-sm text-gray-500 mb-6">{{ $t('checkout.contactInfoSub') }}</p>

    <!-- The VeeForm component now handles state and validation -->
    <!-- The @submit handler will only fire if validation passes -->
    <VeeForm :validation-schema="schema" @submit="onValidSubmit" v-slot="{ meta, values }">
      <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
        
        <!-- First Name Field -->
        <div>
          <label for="first-name" class="block text-sm font-medium text-gray-700">{{ $t('forms.firstName') }}</label>
          <VeeField
            type="text"
            id="first-name"
            name="firstName"
            autocomplete="given-name"
            @input="updateGuestDetails(values)"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="firstName" class="text-sm text-red-600 mt-1" />
        </div>

        <!-- Last Name Field -->
        <div>
          <label for="last-name" class="block text-sm font-medium text-gray-700">{{ $t('forms.lastName') }}</label>
          <VeeField
            type="text"
            id="last-name"
            name="lastName"
            autocomplete="family-name"
            @input="updateGuestDetails(values)"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="lastName" class="text-sm text-red-600 mt-1" />
        </div>

        <!-- Email Field -->
        <div class="sm:col-span-2">
          <label for="email" class="block text-sm font-medium text-gray-700">{{ $t('forms.email') }}</label>
          <VeeField
            type="email"
            name="email"
            id="email"
            autocomplete="email"
            @input="updateGuestDetails(values)"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="email" class="text-sm text-red-600 mt-1" />
        </div>
      </div>

      <!-- Create Account Checkbox -->
      <div class="mt-6">
          <div class="relative flex items-start">
              <div class="flex h-5 items-center">
                  <VeeField
                      type="checkbox"
                      id="createAccount"
                      name="createAccount"
                      @change="updateGuestDetails(values, $event.target.checked)"
                      class="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
              </div>
              <div class="ml-3 text-sm">
                  <label for="createAccount" class="font-medium text-gray-700">{{ $t('checkout.createAccountPrompt') }}</label>
              </div>
          </div>
      </div>

      <!-- Password fields - shown conditionally -->
      <div v-if="values.createAccount" class="mt-6 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
          <div>
              <label for="password" class="block text-sm font-medium text-gray-700">{{ $t('forms.password') }}</label>
              <VeeField
                  type="password"
                  name="password"
                  id="password"
                  autocomplete="new-password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
              />
              <VeeErrorMessage name="password" class="text-sm text-red-600 mt-1" />
          </div>
          <div>
              <label for="passwordConfirmation" class="block text-sm font-medium text-gray-700">{{ $t('forms.passwordConfirm') }}</label>
              <VeeField
                  type="password"
                  name="passwordConfirmation"
                  id="passwordConfirmation"
                  autocomplete="new-password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
              />
              <VeeErrorMessage name="passwordConfirmation" class="text-sm text-red-600 mt-1" />
          </div>
      </div>
      
    </VeeForm>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import * as yup from 'yup';

const { t } = useI18n();

// --- Props and Emits ---
const props = defineProps({
  guestDetails: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:guestDetails', 'update:isValid']);

// --- Validation Schema ---
// The schema is now dynamic. It changes based on whether the 'createAccount' checkbox is ticked.
const schema = computed(() => yup.object({
  firstName: yup.string().required(t('validation.required')),
  lastName: yup.string().required(t('validation.required')),
  email: yup.string().required(t('validation.required')).email(t('validation.email')),
  createAccount: yup.boolean(),
  // `when` makes the password fields required only if `createAccount` is true.
  password: yup.string().when('createAccount', {
      is: true,
      then: (schema) => schema.required(t('validation.required')).min(8, t('validation.minLength', { min: 8 })),
      otherwise: (schema) => schema.optional(),
  }),
  passwordConfirmation: yup.string().when('createAccount', {
      is: true,
      then: (schema) => schema.required(t('validation.required')).oneOf([yup.ref('password')], t('validation.passwordMatch')),
      otherwise: (schema) => schema.optional(),
  }),
}));

// --- Form State & Event Handlers ---
const updateGuestDetails = (formValues, createAccountState = null) => {
    // Create a new object to emit to avoid direct prop mutation issues
    const updatedDetails = {
        ...formValues,
        // If createAccountState is provided (from checkbox change), use it.
        // Otherwise, use the value from the form.
        createAccount: createAccountState !== null ? createAccountState : formValues.createAccount,
    };
    emit('update:guestDetails', updatedDetails);
    
    // Check and emit validity
    schema.value.isValid(updatedDetails).then(isValid => {
        emit('update:isValid', isValid);
    });
};

// This function is only called when the form is submitted AND valid.
const onValidSubmit = (values) => {
  // The parent component handles the actual submission logic.
  // We just ensure the data is up-to-date.
  updateGuestDetails(values);
};
</script>