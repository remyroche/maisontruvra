<template>
  <VeeForm @submit="onSubmit" :validation-schema="schema" v-slot="{ isSubmitting, meta }">
    <div v-if="successMessage" class="p-4 mb-4 text-sm text-green-700 bg-green-100 rounded-lg" role="alert">
      {{ successMessage }}
    </div>

    <div class="space-y-6" v-if="!successMessage">
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <!-- Name Field -->
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700">{{ $t('forms.name') }}</label>
          <VeeField
            type="text"
            name="name"
            id="name"
            autocomplete="name"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="name" class="text-sm text-red-600 mt-1" />
        </div>

        <!-- Email Field -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">{{ $t('forms.email') }}</label>
          <VeeField
            type="email"
            name="email"
            id="email"
            autocomplete="email"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="email" class="text-sm text-red-600 mt-1" />
        </div>
      </div>

      <!-- Subject Field -->
      <div>
        <label for="subject" class="block text-sm font-medium text-gray-700">{{ $t('forms.subject') }}</label>
        <VeeField
          type="text"
          name="subject"
          id="subject"
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
        />
        <VeeErrorMessage name="subject" class="text-sm text-red-600 mt-1" />
      </div>
      
      <!-- Message Field -->
      <div>
        <label for="message" class="block text-sm font-medium text-gray-700">{{ $t('forms.message') }}</label>
        <VeeField
          as="textarea"
          name="message"
          id="message"
          rows="4"
          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm"
        />
        <VeeErrorMessage name="message" class="text-sm text-red-600 mt-1" />
      </div>

       <div v-if="apiError" class="mt-4 text-center text-sm text-red-600">
          {{ apiError }}
       </div>

      <div class="text-right">
        <button
          type="submit"
          :disabled="isSubmitting || !meta.valid"
          class="inline-flex justify-center py-2 px-6 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400"
        >
          <span v-if="isSubmitting" class="loader ease-linear rounded-full border-2 border-t-2 border-gray-200 h-5 w-5 mr-3"></span>
          {{ $t('forms.sendMessage') }}
        </button>
      </div>
    </div>
  </VeeForm>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import * as yup from 'yup';
import api from '@/services/api'; // Assuming api service is correctly set up

const { t } = useI18n();

const apiError = ref(null);
const successMessage = ref(null);

// --- Validation Schema ---
const schema = yup.object({
  name: yup.string().required(t('validation.required')),
  email: yup.string().required(t('validation.required')).email(t('validation.email')),
  subject: yup.string().required(t('validation.required')).min(5, t('validation.minLength', { min: 5 })),
  message: yup.string().required(t('validation.required')).min(10, t('validation.minLength', { min: 10 })),
});

// --- Event Handlers ---
const onSubmit = async (values, { resetForm }) => {
  apiError.value = null;
  successMessage.value = null;

  try {
    // NOTE: A '/contact' endpoint needs to be created on the backend.
    // This is a placeholder for that API call.
    await api.submitContactForm(values); 
    
    successMessage.value = t('contact.success');
    resetForm();

  } catch (error) {
    apiError.value = error.response?.data?.message || t('errors.generic');
  }
};
</script>

<style scoped>
.loader {
  border-top-color: white;
  animation: spinner 1.5s linear infinite;
}

@keyframes spinner {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>