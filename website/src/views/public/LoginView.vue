<template>
  <div class="bg-gray-50">
    <div class="max-w-2xl mx-auto py-16 px-4 sm:py-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <div class="max-w-lg mx-auto">
        <h1 class="text-3xl font-extrabold text-center text-gray-900">{{ $t('auth.login') }}</h1>
        <p class="mt-4 text-center text-sm text-gray-600">
          {{ $t('auth.noAccount') }}
          <router-link :to="{ name: 'Register' }" class="font-medium text-primary hover:text-primary-dark">
            {{ $t('auth.createAccount') }}
          </router-link>
        </p>

        <div class="mt-8 bg-white p-8 shadow rounded-lg">
          <UnifiedLoginForm @login-success="onLoginSuccess" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import UnifiedLoginForm from '@/components/auth/UnifiedLoginForm.vue';

const router = useRouter();

const onLoginSuccess = () => {
  // Redirect to the account dashboard after a successful login
  router.push({ name: 'Dashboard' });
};
</script>