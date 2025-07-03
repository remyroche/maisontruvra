<template>
  <div class="unified-login-form">
    <!-- Step 1: Email and Password -->
    <div v-if="!requires2FA">
      <h3 class="text-lg font-medium text-gray-900 mb-4">
        {{ $t('auth.signIn') }}
      </h3>
      
      <VeeForm @submit="handleLogin" :validation-schema="loginSchema" v-slot="{ isSubmitting }">
        <div class="space-y-4">
          <div>
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

          <div>
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
          </div>
        </div>
        
        <div class="mt-6">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400"
          >
            <span v-if="isSubmitting" class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-5 w-5 mr-3"></span>
            {{ $t('auth.signIn') }}
          </button>
        </div>
        
        <div v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
          {{ errorMessage }}
        </div>
      </VeeForm>
    </div>

    <!-- Step 2: 2FA Verification -->
    <div v-else>
      <h3 class="text-lg font-medium text-gray-900 mb-4">
        {{ $t('auth.twoFactorVerification') }}
      </h3>
      
      <p class="text-sm text-gray-600 mb-4">
        {{ $t('auth.choose2FAMethod') }}
      </p>

      <!-- 2FA Method Selection -->
      <div class="space-y-3 mb-6">
        <button
          v-if="availableMethods.totp"
          @click="selected2FAMethod = 'totp'"
          :class="[
            'w-full flex items-center justify-between p-3 border rounded-lg text-left',
            selected2FAMethod === 'totp' 
              ? 'border-primary bg-primary-50 text-primary' 
              : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <div>
            <div class="font-medium">{{ $t('auth.authenticatorApp') }}</div>
            <div class="text-sm text-gray-500">{{ $t('auth.authenticatorAppDesc') }}</div>
          </div>
          <div v-if="selected2FAMethod === 'totp'" class="text-primary">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
        </button>

        <button
          v-if="availableMethods.magic_link"
          @click="selected2FAMethod = 'magic_link'"
          :class="[
            'w-full flex items-center justify-between p-3 border rounded-lg text-left',
            selected2FAMethod === 'magic_link' 
              ? 'border-primary bg-primary-50 text-primary' 
              : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <div>
            <div class="font-medium">{{ $t('auth.magicLink') }}</div>
            <div class="text-sm text-gray-500">{{ $t('auth.magicLinkDesc') }}</div>
          </div>
          <div v-if="selected2FAMethod === 'magic_link'" class="text-primary">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
        </button>
      </div>

      <!-- TOTP Input -->
      <div v-if="selected2FAMethod === 'totp'">
        <VeeForm @submit="handleTotpVerification" :validation-schema="totpSchema" v-slot="{ isSubmitting }">
          <div class="mb-4">
            <label for="totp_code" class="block text-sm font-medium text-gray-700">
              {{ $t('auth.enterAuthenticatorCode') }}
            </label>
            <VeeField
              type="text"
              name="totp_code"
              id="totp_code"
              maxlength="6"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm text-center"
              placeholder="000000"
            />
            <VeeErrorMessage name="totp_code" class="text-sm text-red-600 mt-1" />
          </div>
          
          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400"
          >
            <span v-if="isSubmitting" class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-5 w-5 mr-3"></span>
            {{ $t('auth.verify') }}
          </button>
        </VeeForm>
      </div>

      <!-- Magic Link Request -->
      <div v-if="selected2FAMethod === 'magic_link'">
        <div class="text-center">
          <div class="mb-4">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          
          <h4 class="text-lg font-medium text-gray-900 mb-2">
            {{ $t('auth.checkYourEmail') }}
          </h4>
          
          <p class="text-sm text-gray-600 mb-4">
            {{ $t('auth.magicLinkSent', { email: userEmail }) }}
          </p>
          
          <button
            @click="requestMagicLink"
            :disabled="magicLinkCooldown > 0"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary bg-primary-100 hover:bg-primary-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-100 disabled:text-gray-400"
          >
            {{ magicLinkCooldown > 0 ? $t('auth.resendIn', { seconds: magicLinkCooldown }) : $t('auth.resendMagicLink') }}
          </button>
        </div>
      </div>

      <!-- Back to login -->
      <div class="mt-6 text-center">
        <button
          @click="goBackToLogin"
          class="text-sm text-primary hover:text-primary-dark"
        >
          {{ $t('auth.backToLogin') }}
        </button>
      </div>

      <div v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useUserStore } from '@/stores/user';
import * as yup from 'yup';

const userStore = useUserStore();
const emit = defineEmits(['login-success']);

// Form state
const errorMessage = ref('');
const requires2FA = ref(false);
const availableMethods = ref({ totp: false, magic_link: false });
const selected2FAMethod = ref('');
const pendingUserId = ref(null);
const userEmail = ref('');
const magicLinkCooldown = ref(0);
let cooldownInterval = null;

// Validation schemas
const loginSchema = yup.object({
  email: yup.string().required('Email is required').email('Invalid email format'),
  password: yup.string().required('Password is required')
});

const totpSchema = yup.object({
  totp_code: yup.string().required('TOTP code is required').length(6, 'Code must be 6 digits')
});

const handleLogin = async (values) => {
  errorMessage.value = '';
  
  try {
    const response = await userStore.loginUnified(values);
    
    if (response.requires_2fa) {
      // Setup 2FA verification
      requires2FA.value = true;
      availableMethods.value = response.available_methods;
      pendingUserId.value = response.user_id;
      userEmail.value = values.email;
      
      // Auto-select method if only one is available
      if (response.available_methods.totp && !response.available_methods.magic_link) {
        selected2FAMethod.value = 'totp';
      } else if (response.available_methods.magic_link && !response.available_methods.totp) {
        selected2FAMethod.value = 'magic_link';
        await requestMagicLink();
      }
    } else {
      // Login successful
      emit('login-success');
    }
  } catch (error) {
    const message = error.response?.data?.error || 'Login failed. Please check your credentials.';
    errorMessage.value = message;
  }
};

const handleTotpVerification = async (values) => {
  errorMessage.value = '';
  
  try {
    await userStore.verify2FA({
      user_id: pendingUserId.value,
      mfa_token: values.totp_code,
      mfa_type: 'totp'
    });
    
    emit('login-success');
  } catch (error) {
    const message = error.response?.data?.error || '2FA verification failed. Please try again.';
    errorMessage.value = message;
  }
};

const requestMagicLink = async () => {
  if (magicLinkCooldown.value > 0) return;
  
  try {
    await userStore.requestMagicLink({ email: userEmail.value });
    
    // Start cooldown
    magicLinkCooldown.value = 60;
    cooldownInterval = setInterval(() => {
      magicLinkCooldown.value--;
      if (magicLinkCooldown.value <= 0) {
        clearInterval(cooldownInterval);
      }
    }, 1000);
  } catch (error) {
    const message = error.response?.data?.error || 'Failed to send magic link.';
    errorMessage.value = message;
  }
};

const goBackToLogin = () => {
  requires2FA.value = false;
  selected2FAMethod.value = '';
  pendingUserId.value = null;
  userEmail.value = '';
  errorMessage.value = '';
  
  if (cooldownInterval) {
    clearInterval(cooldownInterval);
    magicLinkCooldown.value = 0;
  }
};

onUnmounted(() => {
  if (cooldownInterval) {
    clearInterval(cooldownInterval);
  }
});
</script>

<style scoped>
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
</style>