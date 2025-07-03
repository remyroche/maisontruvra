<template>
  <div class="authentication-settings">
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
          {{ $t('auth.authenticationMethods') }}
        </h3>
        
        <div class="space-y-6">
          <!-- Password Section -->
          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 class="text-sm font-medium text-gray-900">{{ $t('auth.password') }}</h4>
              <p class="text-sm text-gray-500">{{ $t('auth.passwordDesc') }}</p>
            </div>
            <button
              @click="showPasswordChange = true"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              {{ $t('auth.changePassword') }}
            </button>
          </div>

          <!-- TOTP Section -->
          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div class="flex-1">
              <div class="flex items-center">
                <h4 class="text-sm font-medium text-gray-900">{{ $t('auth.authenticatorApp') }}</h4>
                <span v-if="user.is_totp_enabled" class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {{ $t('common.enabled') }}
                </span>
                <span v-else class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {{ $t('common.disabled') }}
                </span>
              </div>
              <p class="text-sm text-gray-500">{{ $t('auth.authenticatorAppDesc') }}</p>
            </div>
            <div class="flex space-x-2">
              <button
                v-if="!user.is_totp_enabled"
                @click="setupTotp"
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                {{ $t('auth.enable') }}
              </button>
              <button
                v-else
                @click="showTotpDisable = true"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                {{ $t('auth.disable') }}
              </button>
            </div>
          </div>

          <!-- Magic Link Section -->
          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div class="flex-1">
              <div class="flex items-center">
                <h4 class="text-sm font-medium text-gray-900">{{ $t('auth.magicLink') }}</h4>
                <span v-if="user.is_magic_link_enabled" class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {{ $t('common.enabled') }}
                </span>
                <span v-else class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {{ $t('common.disabled') }}
                </span>
              </div>
              <p class="text-sm text-gray-500">{{ $t('auth.magicLinkDesc') }}</p>
            </div>
            <div class="flex space-x-2">
              <button
                v-if="!user.is_magic_link_enabled"
                @click="enableMagicLink"
                :disabled="isLoading"
                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400"
              >
                {{ $t('auth.enable') }}
              </button>
              <button
                v-else
                @click="showMagicLinkDisable = true"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                {{ $t('auth.disable') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Password Change Modal -->
    <Modal v-if="showPasswordChange" @close="showPasswordChange = false">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          {{ $t('auth.changePassword') }}
        </h3>
        
        <PasswordChangeForm @password-changed="onPasswordChanged" @cancel="showPasswordChange = false" />
      </div>
    </Modal>

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
        
        <VeeForm @submit="confirmTotpSetup" :validation-schema="totpSchema" v-slot="{ isSubmitting }">
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
              {{ $t('common.cancel') }}
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="px-4 py-2 text-sm font-medium text-white bg-primary border border-transparent rounded-md hover:bg-primary-dark disabled:bg-gray-400"
            >
              {{ $t('auth.confirm') }}
            </button>
          </div>
        </VeeForm>
      </div>
    </Modal>

    <!-- TOTP Disable Modal -->
    <Modal v-if="showTotpDisable" @close="showTotpDisable = false">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          {{ $t('auth.disableAuthenticator') }}
        </h3>
        
        <p class="text-sm text-gray-600 mb-4">
          {{ $t('auth.disableAuthenticatorDesc') }}
        </p>
        
        <VeeForm @submit="disableTotp" :validation-schema="disableTotpSchema" v-slot="{ isSubmitting }">
          <div class="space-y-4">
            <div>
              <label for="current_password" class="block text-sm font-medium text-gray-700">
                {{ $t('auth.currentPassword') }}
              </label>
              <VeeField
                type="password"
                name="current_password"
                id="current_password"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              />
              <VeeErrorMessage name="current_password" class="text-sm text-red-600 mt-1" />
            </div>
            
            <div>
              <label for="totp_code" class="block text-sm font-medium text-gray-700">
                {{ $t('auth.enterCurrentCode') }}
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
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="showTotpDisable = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 disabled:bg-gray-400"
            >
              {{ $t('auth.disable') }}
            </button>
          </div>
        </VeeForm>
      </div>
    </Modal>

    <!-- Magic Link Disable Modal -->
    <Modal v-if="showMagicLinkDisable" @close="showMagicLinkDisable = false">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          {{ $t('auth.disableMagicLink') }}
        </h3>
        
        <p class="text-sm text-gray-600 mb-4">
          {{ $t('auth.disableMagicLinkDesc') }}
        </p>
        
        <div class="text-center mb-4">
          <button
            @click="requestDisableMagicLink"
            :disabled="magicLinkCooldown > 0 || isLoading"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400"
          >
            {{ magicLinkCooldown > 0 ? $t('auth.resendIn', { seconds: magicLinkCooldown }) : $t('auth.sendDisableMagicLink') }}
          </button>
        </div>
        
        <p class="text-xs text-gray-500 text-center">
          {{ $t('auth.clickMagicLinkToDisable') }}
        </p>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            @click="showMagicLinkDisable = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {{ $t('common.cancel') }}
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import * as yup from 'yup';
import Modal from '@/components/ui/Modal.vue';
import PasswordChangeForm from './PasswordChangeForm.vue';

const userStore = useUserStore();
const notificationStore = useNotificationStore();

// Component state
const isLoading = ref(false);
const showPasswordChange = ref(false);
const showTotpSetup = ref(false);
const showTotpDisable = ref(false);
const showMagicLinkDisable = ref(false);
const totpSecret = ref('');
const totpQrCode = ref('');
const magicLinkCooldown = ref(0);
let cooldownInterval = null;

// Computed
const user = computed(() => userStore.user);

// Validation schemas
const totpSchema = yup.object({
  totp_code: yup.string().required('TOTP code is required').length(6, 'Code must be 6 digits')
});

const disableTotpSchema = yup.object({
  current_password: yup.string().required('Current password is required'),
  totp_code: yup.string().required('TOTP code is required').length(6, 'Code must be 6 digits')
});

// Methods
const setupTotp = async () => {
  isLoading.value = true;
  try {
    const response = await userStore.setupTotp();
    totpSecret.value = response.secret;
    totpQrCode.value = response.qr_code;
    showTotpSetup.value = true;
  } catch (error) {
    const message = error.response?.data?.error || 'Failed to setup TOTP';
    notificationStore.addNotification(message, 'error');
  } finally {
    isLoading.value = false;
  }
};

const confirmTotpSetup = async (values) => {
  try {
    await userStore.confirmTotpSetup(values.totp_code);
    showTotpSetup.value = false;
    notificationStore.addNotification('Authenticator app enabled successfully', 'success');
    await userStore.checkAuthStatus(); // Refresh user data
  } catch (error) {
    const message = error.response?.data?.error || 'Failed to confirm TOTP setup';
    notificationStore.addNotification(message, 'error');
  }
};

const disableTotp = async (values) => {
  try {
    await userStore.updateAuthMethod({
      action: 'disable_totp',
      current_password: values.current_password,
      totp_code: values.totp_code
    });
    showTotpDisable.value = false;
    notificationStore.addNotification('Authenticator app disabled successfully', 'success');
    await userStore.checkAuthStatus(); // Refresh user data
  } catch (error) {
    const message = error.response?.data?.error || 'Failed to disable TOTP';
    notificationStore.addNotification(message, 'error');
  }
};

const enableMagicLink = async () => {
  isLoading.value = true;
  try {
    await userStore.updateAuthMethod({
      action: 'enable_magic_link',
      current_password: await promptForPassword()
    });
    notificationStore.addNotification('Magic link enabled successfully', 'success');
    await userStore.checkAuthStatus(); // Refresh user data
  } catch (error) {
    const message = error.response?.data?.error || 'Failed to enable magic link';
    notificationStore.addNotification(message, 'error');
  } finally {
    isLoading.value = false;
  }
};

const requestDisableMagicLink = async () => {
  if (magicLinkCooldown.value > 0) return;
  
  isLoading.value = true;
  try {
    // This would send a magic link to disable the feature
    await userStore.requestMagicLink({ email: user.value.email });
    
    // Start cooldown
    magicLinkCooldown.value = 60;
    cooldownInterval = setInterval(() => {
      magicLinkCooldown.value--;
      if (magicLinkCooldown.value <= 0) {
        clearInterval(cooldownInterval);
      }
    }, 1000);
    
    notificationStore.addNotification('Magic link sent to your email', 'success');
  } catch (error) {
    const message = error.response?.data?.error || 'Failed to send magic link';
    notificationStore.addNotification(message, 'error');
  } finally {
    isLoading.value = false;
  }
};

const promptForPassword = () => {
  return new Promise((resolve, reject) => {
    const password = prompt('Please enter your current password:');
    if (password) {
      resolve(password);
    } else {
      reject(new Error('Password required'));
    }
  });
};

const onPasswordChanged = () => {
  showPasswordChange.value = false;
  notificationStore.addNotification('Password changed successfully', 'success');
};

onUnmounted(() => {
  if (cooldownInterval) {
    clearInterval(cooldownInterval);
  }
});
</script>