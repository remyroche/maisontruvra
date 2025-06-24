<template>
  <div class="flex min-h-full flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">Réinitialiser votre mot de passe</h2>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <Form @submit="handleReset" class="space-y-6">
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Nouveau mot de passe</label>
            <Field name="password" type="password" id="password" v-model="password" rules="required|min:8" class="mt-1 block w-full input" />
            <ErrorMessage name="password" class="text-sm text-red-600" />
          </div>

          <div>
            <label for="password_confirmation" class="block text-sm font-medium text-gray-700">Confirmer le nouveau mot de passe</label>
            <Field name="password_confirmation" type="password" id="password_confirmation" rules="required|confirmed:@password" class="mt-1 block w-full input" />
            <ErrorMessage name="password_confirmation" class="text-sm text-red-600" />
          </div>

          <div>
            <button type="submit" :disabled="loading" class="w-full btn-primary">
              Mettre à jour le mot de passe
            </button>
          </div>
        </Form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Form, Field, ErrorMessage } from 'vee-validate';
import apiClient from '../../js/api-client';
import { useNotificationStore } from '../../js/stores/notification';

const route = useRoute();
const router = useRouter();
const notificationStore = useNotificationStore();

const password = ref('');
const loading = ref(false);

const handleReset = async () => {
    loading.value = true;
    try {
        const token = route.params.token;
        await apiClient.b2bResetPassword(token, password.value); // New apiClient method needed
        notificationStore.showNotification("Votre mot de passe a été réinitialisé avec succès.", 'success');
        router.push('/professionnels');
    } catch (error) {
        notificationStore.showNotification(error.data?.error || "Le lien de réinitialisation est invalide ou a expiré.", 'error');
    } finally {
        loading.value = false;
    }
};
</script>
