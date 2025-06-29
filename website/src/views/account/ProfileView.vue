<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900">{{ $t('account.profile.title') }}</h2>
    
    <!-- Profile Information Form -->
    <div class="mt-8 bg-white p-6 shadow rounded-lg">
      <h3 class="text-lg font-medium leading-6 text-gray-900">{{ $t('account.profile.contactInfo') }}</h3>
      <VeeForm v-if="user" class="mt-6" @submit="onUpdateProfile" :initial-values="user" :validation-schema="profileSchema" v-slot="{ isSubmitting }">
        <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
          <!-- First Name -->
          <div>
            <label for="firstName" class="block text-sm font-medium text-gray-700">{{ $t('forms.firstName') }}</label>
            <VeeField type="text" name="first_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="first_name" class="text-sm text-red-600 mt-1" />
          </div>

          <!-- Last Name -->
          <div>
            <label for="lastName" class="block text-sm font-medium text-gray-700">{{ $t('forms.lastName') }}</label>
            <VeeField type="text" name="last_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="last_name" class="text-sm text-red-600 mt-1" />
          </div>

          <!-- Email (read-only) -->
          <div class="sm:col-span-2">
             <label for="email" class="block text-sm font-medium text-gray-700">{{ $t('forms.email') }}</label>
            <VeeField type="email" name="email" readonly class="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-100 sm:text-sm" />
          </div>

           <!-- Phone Number -->
          <div class="sm:col-span-2">
            <label for="phone_number" class="block text-sm font-medium text-gray-700">{{ $t('forms.phone') }} ({{ $t('forms.optional') }})</label>
            <VeeField type="text" name="phone_number" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
            <VeeErrorMessage name="phone_number" class="text-sm text-red-600 mt-1" />
          </div>
        </div>
        <div class="mt-6 text-right">
          <button type="submit" :disabled="isSubmitting" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400">
            {{ $t('forms.saveChanges') }}
          </button>
        </div>
      </VeeForm>
    </div>

    <!-- Change Password Form -->
    <div class="mt-12 bg-white p-6 shadow rounded-lg">
      <h3 class="text-lg font-medium leading-6 text-gray-900">{{ $t('account.profile.changePassword') }}</h3>
      <PasswordChangeForm class="mt-6" />
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import { useI18n } from 'vue-i18n';
import * as yup from 'yup';
import PasswordChangeForm from '@/components/auth/PasswordChangeForm.vue';

const { t } = useI18n();
const userStore = useUserStore();
const notificationStore = useNotificationStore();

const user = computed(() => userStore.user);

const profileSchema = yup.object({
  first_name: yup.string().required(t('validation.required')),
  last_name: yup.string().required(t('validation.required')),
  email: yup.string().email().required(), // Should be read-only anyway
  phone_number: yup.string().nullable(),
});

const onUpdateProfile = async (values) => {
  try {
    await userStore.updateProfile(values);
    notificationStore.showNotification(t('account.profile.updateSuccess'), 'success');
  } catch (error) {
    // The api.js interceptor will show the error notification
    console.error("Failed to update profile:", error);
  }
};
</script>