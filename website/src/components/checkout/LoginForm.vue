<template>
  <div class="login-form">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Se connecter</h3>
    <VeeForm @submit="onSubmit" :validation-schema="schema" v-slot="{ isSubmitting }">
      <div class="space-y-4">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Adresse e-mail</label>
          <VeeField
            type="email"
            name="email"
            id="email"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
          />
          <VeeErrorMessage name="email" class="text-sm text-red-600 mt-1" />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">Mot de passe</label>
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
          Se connecter
        </button>
      </div>
      
       <div v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
          {{ errorMessage }}
        </div>
    </VeeForm>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import * as yup from 'yup';

const userStore = useUserStore();
const emit = defineEmits(['login-success']);
const errorMessage = ref(null);

// Define validation schema with Yup
const schema = yup.object({
  email: yup.string().required('L\'adresse e-mail est requise').email('L\'adresse e-mail est invalide'),
  password: yup.string().required('Le mot de passe est requis'),
});

const onSubmit = async (values, { setErrors }) => {
  errorMessage.ref = null;
  try {
    await userStore.login(values);
    emit('login-success');
  } catch (error) {
    const message = error.response?.data?.message || 'Une erreur est survenue.';
    errorMessage.ref = message;
    // You can also set specific field errors if the API returns them
    if (error.response?.data?.errors) {
       setErrors(error.response.data.errors);
    }
  }
};
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
