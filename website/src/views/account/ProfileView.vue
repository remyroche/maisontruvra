<template>
  <div class="space-y-12">
    <h2 class="text-2xl font-bold text-gray-900">{{ $t('account.profile.title') }}</h2>
    
    <!-- Profile Information Form -->
    <div class="bg-white p-6 shadow rounded-lg">
      <h3 class="text-lg font-medium leading-6 text-gray-900">{{ $t('account.profile.contactInfo') }}</h3>
      <VeeForm v-if="user" class="mt-6" @submit="onUpdateProfile" :initial-values="user" :validation-schema="profileSchema" v-slot="{ isSubmitting }">
        <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
          <!-- Form fields from previous turn -->
          <div>
            <label for="firstName" class="block text-sm font-medium text-gray-700">{{ $t('forms.firstName') }}</label>
            <VeeField type="text" name="first_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
            <VeeErrorMessage name="first_name" class="text-sm text-red-600 mt-1" />
          </div>
          <div>
            <label for="lastName" class="block text-sm font-medium text-gray-700">{{ $t('forms.lastName') }}</label>
            <VeeField type="text" name="last_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
            <VeeErrorMessage name="last_name" class="text-sm text-red-600 mt-1" />
          </div>
          <div class="sm:col-span-2">
            <label for="email" class="block text-sm font-medium text-gray-700">{{ $t('forms.email') }}</label>
            <VeeField type="email" name="email" readonly class="mt-1 block w-full border-gray-300 rounded-md shadow-sm bg-gray-100" />
          </div>
        </div>
        <div class="mt-6 text-right">
          <button type="submit" :disabled="isSubmitting" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark disabled:bg-gray-400">
            {{ $t('forms.saveChanges') }}
          </button>
        </div>
      </VeeForm>
    </div>

    <!-- B2C Address Manager -->
    <B2CAddressManager />

    <!-- Authentication Settings -->
    <AuthenticationSettings />

    <!-- Delete Account Section -->
    <div class="bg-white p-6 rounded-lg shadow border border-red-200">
      <h3 class="text-lg font-bold text-red-700">Delete Account</h3>
      <p class="text-gray-600 mt-2 mb-4">This action will schedule your account for deletion. This cannot be undone.</p>
      <button @click="showConfirmModal = true" class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">
        Request Account Deletion
      </button>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showConfirmModal" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center p-4">
        <!-- Modal content from previous turn -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import { useI18n } from 'vue-i18n';
import { object as yupObject, string as yupString } from 'yup';
import { Form as VeeForm, Field as VeeField, ErrorMessage as VeeErrorMessage } from 'vee-validate';
import PasswordChangeForm from '@/components/auth/PasswordChangeForm.vue';
import B2CAddressManager from '@/components/account/B2CAddressManager.vue';
import AuthenticationSettings from '@/components/auth/AuthenticationSettings.vue';

const { t } = useI18n();
const userStore = useUserStore();
const notificationStore = useNotificationStore();
const router = useRouter();

const user = computed(() => userStore.user);
const showConfirmModal = ref(false);

const profileSchema = yupObject({
  first_name: yupString().required(t('validation.required')),
  last_name: yupString().required(t('validation.required')),
  email: yupString().email().required(),
});

const onUpdateProfile = async (values) => {
  const success = await userStore.updateProfile(values);
  if (success) {
      notificationStore.addNotification(t('account.profile.updateSuccess'), 'success');
  }
};

async function confirmDeletion() {
  showConfirmModal.value = false;
  const success = await userStore.deleteAccount();
  if (success) {
    router.push('/');
  }
}
</script>
