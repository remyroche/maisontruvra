<template>
  <div class="unified-register-form">
    <h2 class="text-2xl font-bold leading-9 tracking-tight text-gray-900 mb-6">
      {{ $t('auth.createAccount') }}
    </h2>

    <VeeForm @submit="handleRegister" :validation-schema="schema" v-slot="{ isSubmitting }">
      <!-- User Type Selection -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-3">
          {{ $t('auth.accountType') }}
        </label>
        <div class="grid grid-cols-2 gap-4">
          <label class="relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none">
            <VeeField
              type="radio"
              name="user_type"
              value="b2c"
              class="sr-only"
            />
            <span class="flex flex-1">
              <span class="flex flex-col">
                <span class="block text-sm font-medium text-gray-900">
                  {{ $t('auth.personalAccount') }}
                </span>
                <span class="mt-1 flex items-center text-sm text-gray-500">
                  {{ $t('auth.personalAccountDesc') }}
                </span>
              </span>
            </span>
          </label>
          
          <label class="relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none">
            <VeeField
              type="radio"
              name="user_type"
              value="b2b"
              class="sr-only"
            />
            <span class="flex flex-1">
              <span class="flex flex-col">
                <span class="block text-sm font-medium text-gray-900">
                  {{ $t('auth.businessAccount') }}
                </span>
                <span class="mt-1 flex items-center text-sm text-gray-500">
                  {{ $t('auth.businessAccountDesc') }}
                </span>
              </span>
            </span>
          </label>
        </div>
        <VeeErrorMessage name="user_type" class="text-sm text-red-600 mt-1" />
      </div>

      <!-- Basic Information -->
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label for="first_name" class="block text-sm font-medium text-gray-700">
            {{ $t('auth.firstName') }}
          </label>
          <VeeField
            type="text"
            name="first_name"
            id="first_name"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="first_name" class="text-sm text-red-600 mt-1" />
        </div>

        <div>
          <label for="last_name" class="block text-sm font-medium text-gray-700">
            {{ $t('auth.lastName') }}
          </label>
          <VeeField
            type="text"
            name="last_name"
            id="last_name"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="last_name" class="text-sm text-red-600 mt-1" />
        </div>
      </div>

      <div class="mb-4">
        <label for="email" class="block text-sm font-medium text-gray-700">
          {{ $t('auth.email') }}
        </label>
        <VeeField
          type="email"
          name="email"
          id="email"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
        />
        <VeeErrorMessage name="email" class="text-sm text-red-600 mt-1" />
      </div>

      <div class="mb-6">
        <label for="password" class="block text-sm font-medium text-gray-700">
          {{ $t('auth.password') }}
        </label>
        <VeeField
          type="password"
          name="password"
          id="password"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
        />
        <VeeErrorMessage name="password" class="text-sm text-red-600 mt-1" />
        <PasswordValidator :password="watchedPassword" class="mt-2" />
      </div>

      <!-- 2FA Setup (Optional) -->
      <div class="mb-6 p-4 bg-gray-50 rounded-lg">
        <div class="flex items-center mb-3">
          <VeeField
            type="checkbox"
            name="setup_2fa"
            id="setup_2fa"
            class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
          />
          <label for="setup_2fa" class="ml-2 block text-sm text-gray-900">
            {{ $t('auth.setup2FA') }}
          </label>
        </div>
        
        <div v-if="watchedSetup2FA" class="ml-6">
          <p class="text-sm text-gray-600 mb-3">
            {{ $t('auth.choose2FAMethod') }}
          </p>
          
          <div class="space-y-2">
            <label class="flex items-center">
              <VeeField
                type="radio"
                name="two_fa_method"
                value="totp"
                class="h-4 w-4 text-primary focus:ring-primary border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">
                {{ $t('auth.authenticatorApp') }}
              </span>
            </label>
            
            <label class="flex items-center">
              <VeeField
                type="radio"
                name="two_fa_method"
                value="magic_link"
                class="h-4 w-4 text-primary focus:ring-primary border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">
                {{ $t('auth.magicLink') }}
              </span>
            </label>
          </div>
          <VeeErrorMessage name="two_fa_method" class="text-sm text-red-600 mt-1" />
        </div>
      </div>

      <!-- Submit Button -->
      <div>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="flex w-full justify-center rounded-md bg-primary px-3 py-2 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-primary-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:bg-gray-400"
        >
          <span v-if="isSubmitting" class="loader ease-linear rounded-full border-2 border-t-2 border-gray-200 h-4 w-4 mr-2"></span>
          {{ $t('auth.createAccount') }}
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
        {{ errorMessage }}
      </div>
    </VeeForm>

    <!-- TOTP Setup Modal -->
    <Modal v-if="showTotpSetup" @close="showTotpSetup = false">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          {{ $t('auth.setupAuthenticator') }}
        </h3>
        
        <div class="text-center mb-4">
          <img :src="totpQrCode" alt="QR Code" class="mx-auto mb-4" />
          <p class="text-sm text-gray-600 mb-2">
            {{ $t('auth.scanQrCode') }}
          </p>
          <p class="text-xs text-gray-500 font-mono bg-gray-100 p-2 rounded">
            {{ totpSecret }}
          </p>
        </div>
        
        <VeeForm @submit="confirmTotpSetup" :validation-schema="totpSchema" v-slot="{ isSubmitting: isConfirming }">
          <div class="mb-4">
            <label for="totp_code" class="block text-sm font-medium text-gray-700">
              {{ $t('auth.enterCode') }}
            </label>
            <VeeField
              type="text"
              name="totp_code"
              id="totp_code"
              maxlength="6"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm text-center"
            />
            <VeeErrorMessage name="totp_code" class="text-sm text-red-600 mt-1" />
          </div>
          
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showTotpSetup = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              {{ $t('common.skip') }}
            </button>
            <button
              type="submit"
              :disabled="isConfirming"
              class="px-4 py-2 text-sm font-medium text-white bg-primary border border-transparent rounded-md hover:bg-primary-dark disabled:bg-gray-400"
            >
              {{ $t('auth.confirm') }}
            </button>
          </div>
        </VeeForm>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import * as yup from 'yup';
import PasswordValidator from './PasswordValidator.vue';
import Modal from '@/components/ui/Modal.vue';

const router = useRouter();
const userStore = useUserStore();
const notificationStore = useNotificationStore();

// Form state
const errorMessage = ref('');
const showTotpSetup = ref(false);
const totpSecret = ref('');
const totpQrCode = ref('');

// Watch form values
const watchedPassword = ref('');
const watchedSetup2FA = ref(false);

// Validation schemas
const schema = yup.object({
  user_type: yup.string().required('Please select an account type').oneOf(['b2c', 'b2b']),
  first_name: yup.string().required('First name is required').min(1).max(50),
  last_name: yup.string().required('Last name is required').min(1).max(50),
  email: yup.string().required('Email is required').email('Invalid email format'),
  password: yup.string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .matches(/[a-z]/, 'Password must contain at least one lowercase letter')
    .matches(/\d/, 'Password must contain at least one digit'),
  setup_2fa: yup.boolean(),
  two_fa_method: yup.string().when('setup_2fa', {
    is: true,
    then: yup.string().required('Please select a 2FA method').oneOf(['totp', 'magic_link']),
    otherwise: yup.string().nullable()
  })
});

const totpSchema = yup.object({
  totp_code: yup.string().required('TOTP code is required').length(6, 'Code must be 6 digits')
});

// Watch password for validator
watch(() => watchedPassword.value, (newVal) => {
  // This will be updated by VeeValidate
});

// Watch 2FA setup checkbox
watch(() => watchedSetup2FA.value, (newVal) => {
  // This will be updated by VeeValidate
});

const handleRegister = async (values) => {
  errorMessage.value = '';
  
  try {
    const response = await userStore.registerUnified(values);
    
    if (response.totp_setup && values.setup_2fa && values.two_fa_method === 'totp') {
      // Show TOTP setup modal
      totpSecret.value = response.totp_setup.secret;
      totpQrCode.value = response.totp_setup.qr_code;
      showTotpSetup.value = true;
    } else {
      // Registration complete
      notificationStore.addNotification(
        'Registration successful! Please check your email to verify your account.',
        'success'
      );
      router.push({ name: 'Login' });
    }
  } catch (error) {
    const message = error.response?.data?.error || 'Registration failed. Please try again.';
    errorMessage.value = message;
  }
};

const confirmTotpSetup = async (values) => {
  try {
    await userStore.confirmTotpSetup(values.totp_code);
    showTotpSetup.value = false;
    notificationStore.addNotification(
      'Registration and 2FA setup completed! Please check your email to verify your account.',
      'success'
    );
    router.push({ name: 'Login' });
  } catch (error) {
    const message = error.response?.data?.error || 'TOTP setup failed. Please try again.';
    notificationStore.addNotification(message, 'error');
  }
};
</script>
<style lang="postcss" scoped>
.loader {
  border-top-color: #3498db;
  -webkit-animation: spinner 1.5s linear infinite;
  animation: spinner 1.5s linear infinite;
}

@-webkit-keyframes spinner {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spinner {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Radio button styling */
input[type="radio"]:checked + span {
  @apply ring-2 ring-primary;
}
</style>