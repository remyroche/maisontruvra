<template>
  <div class="bg-white rounded-lg shadow-sm border p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Connexion</h3>
    
    <form @submit.prevent="handleLogin" class="space-y-4">
      <!-- Email -->
      <div>
        <label for="loginEmail" class="block text-sm font-medium text-gray-700 mb-1">
          Adresse email *
        </label>
        <input 
          id="loginEmail"
          v-model="loginForm.email"
          type="email" 
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
          :class="{ 'border-red-500': errors.email }"
          placeholder="votre@email.com"
          @blur="validateEmail"
        >
        <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
      </div>

      <!-- Password -->
      <div>
        <label for="loginPassword" class="block text-sm font-medium text-gray-700 mb-1">
          Mot de passe *
        </label>
        <div class="relative">
          <input 
            id="loginPassword"
            v-model="loginForm.password"
            :type="showPassword ? 'text' : 'password'"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 focus:ring-brand-burgundy focus:border-brand-burgundy"
            :class="{ 'border-red-500': errors.password }"
            @blur="validatePassword"
          >
          <button 
            type="button"
            @click="showPassword = !showPassword"
            class="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <svg v-if="showPassword" class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
            </svg>
            <svg v-else class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
        </div>
        <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
      </div>

      <!-- Remember Me -->
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <input 
            id="rememberMe"
            v-model="loginForm.rememberMe"
            type="checkbox" 
            class="text-brand-burgundy focus:ring-brand-burgundy"
          >
          <label for="rememberMe" class="ml-2 text-sm text-gray-700">
            Se souvenir de moi
          </label>
        </div>
        
        <button 
          type="button"
          @click="showForgotPassword = true"
          class="text-sm text-brand-burgundy hover:underline"
        >
          Mot de passe oublié ?
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="loginError" class="p-3 bg-red-50 border border-red-200 rounded-md">
        <div class="flex">
          <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="ml-2 text-sm text-red-600">{{ loginError }}</p>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="pt-4">
        <button 
          type="submit" 
          :disabled="!isFormValid || isLoggingIn"
          class="w-full bg-brand-burgundy text-white py-3 px-4 rounded-md font-medium hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isLoggingIn ? 'Connexion...' : 'Se connecter' }}
        </button>
      </div>

      <!-- Guest Checkout Link -->
      <div class="text-center pt-4 border-t">
        <p class="text-sm text-gray-600">
          Pas encore de compte ?
          <button 
            type="button"
            @click="$emit('switch-to-guest')"
            class="text-brand-burgundy hover:underline font-medium"
          >
            Continuer en tant qu'invité
          </button>
        </p>
      </div>
    </form>

    <!-- Forgot Password Modal -->
    <Modal v-if="showForgotPassword" @close="showForgotPassword = false">
      <template #header>
        <h3 class="text-lg font-semibold">Réinitialiser le mot de passe</h3>
      </template>
      
      <form @submit.prevent="handleForgotPassword" class="space-y-4">
        <div>
          <label for="resetEmail" class="block text-sm font-medium text-gray-700 mb-1">
            Adresse email
          </label>
          <input 
            id="resetEmail"
            v-model="resetForm.email"
            type="email" 
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            placeholder="votre@email.com"
          >
          <p class="mt-1 text-sm text-gray-500">
            Nous vous enverrons un lien pour réinitialiser votre mot de passe.
          </p>
        </div>

        <div v-if="resetError" class="p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ resetError }}</p>
        </div>

        <div v-if="resetSuccess" class="p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-600">{{ resetSuccess }}</p>
        </div>

        <div class="flex justify-end space-x-3 pt-4">
          <button 
            type="button" 
            @click="showForgotPassword = false"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Annuler
          </button>
          <button 
            type="submit" 
            :disabled="!resetForm.email || isResetting"
            class="px-4 py-2 bg-brand-burgundy text-white rounded-md hover:bg-opacity-90 disabled:opacity-50"
          >
            {{ isResetting ? 'Envoi...' : 'Envoyer le lien' }}
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { apiClient } from '@/services/api';
import { useUserStore } from '@/stores/user';
import Modal from '@/components/ui/Modal.vue';

const emit = defineEmits(['login-success', 'switch-to-guest']);

const userStore = useUserStore();

// Form data
const loginForm = ref({
  email: '',
  password: '',
  rememberMe: false
});

const resetForm = ref({
  email: ''
});

// State
const errors = ref({});
const loginError = ref('');
const isLoggingIn = ref(false);
const showPassword = ref(false);
const showForgotPassword = ref(false);
const resetError = ref('');
const resetSuccess = ref('');
const isResetting = ref(false);

// Computed
const isFormValid = computed(() => {
  return loginForm.value.email && 
         loginForm.value.password && 
         Object.keys(errors.value).length === 0;
});

// Validation methods
function validateEmail() {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!loginForm.value.email) {
    errors.value.email = 'L\'adresse email est requise';
  } else if (!emailRegex.test(loginForm.value.email)) {
    errors.value.email = 'Veuillez saisir une adresse email valide';
  } else {
    delete errors.value.email;
  }
}

function validatePassword() {
  if (!loginForm.value.password) {
    errors.value.password = 'Le mot de passe est requis';
  } else {
    delete errors.value.password;
  }
}

// Login handler
async function handleLogin() {
  // Validate form
  validateEmail();
  validatePassword();

  if (!isFormValid.value) {
    return;
  }

  isLoggingIn.value = true;
  loginError.value = '';

  try {
    const response = await apiClient.post('/auth/login', {
      email: loginForm.value.email.trim(),
      password: loginForm.value.password,
      remember_me: loginForm.value.rememberMe
    });

    // Update user store
    await userStore.checkAuthStatus();

    // Emit success event
    emit('login-success', response.user);

  } catch (error) {
    console.error('Login failed:', error);
    
    if (error.response?.status === 401) {
      loginError.value = 'Email ou mot de passe incorrect.';
    } else if (error.response?.status === 429) {
      loginError.value = 'Trop de tentatives de connexion. Veuillez réessayer plus tard.';
    } else if (error.response?.data?.message) {
      loginError.value = error.response.data.message;
    } else {
      loginError.value = 'Une erreur est survenue lors de la connexion. Veuillez réessayer.';
    }
  } finally {
    isLoggingIn.value = false;
  }
}

// Forgot password handler
async function handleForgotPassword() {
  if (!resetForm.value.email) {
    resetError.value = 'Veuillez saisir votre adresse email.';
    return;
  }

  isResetting.value = true;
  resetError.value = '';
  resetSuccess.value = '';

  try {
    await apiClient.post('/auth/forgot-password', {
      email: resetForm.value.email.trim()
    });

    resetSuccess.value = 'Un lien de réinitialisation a été envoyé à votre adresse email.';
    resetForm.value.email = '';

    // Close modal after 3 seconds
    setTimeout(() => {
      showForgotPassword.value = false;
      resetSuccess.value = '';
    }, 3000);

  } catch (error) {
    console.error('Forgot password failed:', error);
    
    if (error.response?.status === 404) {
      resetError.value = 'Aucun compte n\'est associé à cette adresse email.';
    } else if (error.response?.status === 429) {
      resetError.value = 'Trop de demandes. Veuillez réessayer plus tard.';
    } else if (error.response?.data?.message) {
      resetError.value = error.response.data.message;
    } else {
      resetError.value = 'Une erreur est survenue. Veuillez réessayer.';
    }
  } finally {
    isResetting.value = false;
  }
}

// Expose form data for parent component
defineExpose({
  form: computed(() => loginForm.value),
  isValid: isFormValid,
  validate: () => {
    validateEmail();
    validatePassword();
    return isFormValid.value;
  }
});
</script>