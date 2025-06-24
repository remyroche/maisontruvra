<template>
  <div>
    <Form @submit="handleLogin" class="space-y-6">
      <div>
        <label for="login-email" class="block text-sm font-medium text-gray-700">Email</label>
        <Field name="email" type="email" id="login-email" rules="required|email" v-model="email" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        <ErrorMessage name="email" class="text-sm text-red-600" />
      </div>

      <div>
        <label for="login-password" class="block text-sm font-medium text-gray-700">Mot de passe</label>
        <Field name="password" type="password" id="login-password" rules="required" v-model="password" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
        <ErrorMessage name="password" class="text-sm text-red-600" />
      </div>

      <div class="flex items-center justify-between">
        <a href="#" class="text-sm text-indigo-600 hover:text-indigo-500">Mot de passe oublié ?</a>
      </div>

      <div>
        <button type="submit" :disabled="loading" class="flex w-full justify-center btn-primary">
          <span v-if="!loading">Se connecter</span>
          <span v-else>Connexion...</span>
        </button>
      </div>
    </Form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Form, Field, ErrorMessage } from 'vee-validate';
import { useAuthStore } from '../../js/stores/auth';
import { useNotificationStore } from '../../js/stores/notification';

const emit = defineEmits(['success']);

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const email = ref('');
const password = ref('');
const loading = ref(false);

async function handleLogin() {
    loading.value = true;
    try {
        await authStore.login(email.value, password.value);
        notificationStore.showNotification('Connexion réussie !', 'success');
        emit('success'); // Notify parent component
    } catch (error) {
        notificationStore.showNotification(error.data?.error || 'Échec de la connexion', 'error');
    } finally {
        loading.value = false;
    }
}
</script>
