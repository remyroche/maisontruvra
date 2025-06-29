<template>
  <VeeForm @submit="onSubmit" :validation-schema="passwordSchema" v-slot="{ isSubmitting, resetForm }">
    <div class="grid grid-cols-1 gap-y-6">
      <!-- Current Password -->
      <div>
        <label for="currentPassword" class="block text-sm font-medium text-gray-700">{{ $t('forms.currentPassword') }}</label>
        <VeeField type="password" name="currentPassword" id="currentPassword" autocomplete="current-password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
        <VeeErrorMessage name="currentPassword" class="text-sm text-red-600 mt-1" />
      </div>

      <!-- New Password -->
      <div>
        <label for="newPassword" class="block text-sm font-medium text-gray-700">{{ $t('forms.newPassword') }}</label>
        <VeeField type="password" name="newPassword" id="newPassword" autocomplete="new-password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
        <VeeErrorMessage name="newPassword" class="text-sm text-red-600 mt-1" />
      </div>

      <!-- Confirm New Password -->
      <div>
        <label for="newPasswordConfirmation" class="block text-sm font-medium text-gray-700">{{ $t('forms.passwordConfirmNew') }}</label>
        <VeeField type="password" name="newPasswordConfirmation" id="newPasswordConfirmation" autocomplete="new-password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm" />
        <VeeErrorMessage name="newPasswordConfirmation" class="text-sm text-red-600 mt-1" />
      </div>
    </div>

    <div v-if="apiError" class="mt-4 text-sm text-red-600">
      {{ apiError }}
    </div>

    <div class="mt-6 text-right">
      <button type="submit" :disabled="isSubmitting" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400">
        {{ $t('forms.updatePassword') }}
      </button>
    </div>
  </VeeForm>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import { useI18n } from 'vue-i18n';
import * as yup from 'yup';

const { t } = useI18n();
const userStore = useUserStore();
const notificationStore = useNotificationStore();
const apiError = ref(null);

const passwordSchema = yup.object({
  currentPassword: yup.string().required(t('validation.required')),
  newPassword: yup.string().required(t('validation.required')).min(8, t('validation.minLength', { min: 8 })),
  newPasswordConfirmation: yup.string()
    .oneOf([yup.ref('newPassword'), null], t('validation.passwordMatch'))
    .required(t('validation.required')),
});

const onSubmit = async (values, { resetForm }) => {
  apiError.value = null;
  const payload = {
    current_password: values.currentPassword,
    new_password: values.newPassword,
  };
  try {
    await userStore.changePassword(payload);
    notificationStore.showNotification(t('account.profile.passwordUpdateSuccess'), 'success');
    resetForm();
  } catch (error) {
    apiError.value = error.response?.data?.message || t('errors.generic');
  }
};
</script>