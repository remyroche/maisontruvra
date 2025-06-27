<template>
  <div class="mt-6 p-4 bg-gray-100 rounded-lg">
    <h3 class="text-base font-medium text-gray-900">{{ $t('product_unavailable') }}</h3>
    <p class="text-sm text-gray-600 mt-1">{{ $t('stock_notification_prompt') }}</p>
    
    <Form @submit="handleSubmit" :validation-schema="validationSchema" class="mt-4">
      <div v-if="!userStore.isLoggedIn" class="mb-4">
        <label for="email-stock-notification" class="sr-only">{{ $t('email_address') }}</label>
        <Field
          name="email"
          type="email"
          id="email-stock-notification"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
          :placeholder="$t('your_email_placeholder')"
        />
        <ErrorMessage name="email" class="text-sm text-red-600 mt-1" />
      </div>

      <button type="submit" :disabled="isLoading || submitted" class="w-full flex items-center justify-center rounded-md border border-transparent bg-primary py-3 px-8 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed">
        <span v-if="isLoading">{{ $t('sending') }}</span>
        <span v-else-if="submitted" class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>
            {{ $t('notification_registered') }}
        </span>
        <span v-else>{{ $t('notify_me') }}</span>
      </button>
    </Form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useUserStore } from '../../../js/stores/user';
import { useNotificationStore } from '../../../js/stores/notification';
import { apiClient } from '../../../js/api-client';
import { Form, Field, ErrorMessage } from 'vee-validate';
import * as yup from 'yup';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  productId: {
    type: String,
    required: true
  }
});

const userStore = useUserStore();
const notificationStore = useNotificationStore();

const isLoading = ref(false);
const submitted = ref(false);

// Define validation schema using yup
const validationSchema = computed(() => {
    if (!userStore.isLoggedIn) {
        return yup.object({
            email: yup.string().required(t('email_is_required')).email(t('must_be_valid_email')),
        });
    }
    return yup.object({}); // No validation needed for logged-in users
});


async function handleSubmit(values) {
  isLoading.value = true;
  submitted.value = false;
  try {
    // For logged-in users, the payload is empty as the backend identifies them via JWT.
    // For guests, the payload contains the email from the form.
    const payload = userStore.isLoggedIn ? {} : { email: values.email };

    await apiClient.post(`/products/${props.productId}/notify-me`, payload);
    
    submitted.value = true; // Set submitted to true on success
    notificationStore.showNotification({ message: t('stock_notification_success'), type: 'success' });
  } catch (error) {
    const errorMessage = error.response?.data?.error || t('an_error_occurred');
    notificationStore.showNotification({ message: errorMessage, type: 'error' });
  } finally {
    isLoading.value = false;
  }
}
</script>
