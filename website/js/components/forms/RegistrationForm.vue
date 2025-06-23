
<template>
  <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold mb-6 text-center">Créer un compte</h2>
    
    <Form @submit="handleSubmit" :validation-schema="schema">
      <div class="mb-4">
        <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
          Prénom *
        </label>
        <Field
          name="first_name"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.first_name }"
        />
        <ErrorMessage name="first_name" class="text-red-500 text-sm mt-1" />
      </div>

      <div class="mb-4">
        <label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
          Nom *
        </label>
        <Field
          name="last_name"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.last_name }"
        />
        <ErrorMessage name="last_name" class="text-red-500 text-sm mt-1" />
      </div>

      <div class="mb-4">
        <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
          Email *
        </label>
        <Field
          name="email"
          type="email"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.email }"
        />
        <ErrorMessage name="email" class="text-red-500 text-sm mt-1" />
      </div>

      <div class="mb-4">
        <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
          Mot de passe *
        </label>
        <Field
          name="password"
          type="password"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.password }"
        />
        <ErrorMessage name="password" class="text-red-500 text-sm mt-1" />
        <div class="text-xs text-gray-500 mt-1">
          Minimum 8 caractères avec majuscule, minuscule, chiffre et caractère spécial
        </div>
      </div>

      <div class="mb-6">
        <label for="password_confirmation" class="block text-sm font-medium text-gray-700 mb-2">
          Confirmer le mot de passe *
        </label>
        <Field
          name="password_confirmation"
          type="password"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.password_confirmation }"
        />
        <ErrorMessage name="password_confirmation" class="text-red-500 text-sm mt-1" />
      </div>

      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
      >
        <span v-if="isSubmitting">Création en cours...</span>
        <span v-else>Créer mon compte</span>
      </button>
    </Form>
  </div>
</template>

<script setup>
import { Form, Field, ErrorMessage, useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/yup';
import * as yup from 'yup';
import { authService } from '../../auth_service.js';
import { useRouter } from 'vue-router';
import { ref } from 'vue';

const router = useRouter();
const isSubmitting = ref(false);

// Validation schema matching backend rules
const schema = toTypedSchema(
  yup.object({
    first_name: yup
      .string()
      .required('Le prénom est requis')
      .min(2, 'Le prénom doit contenir au moins 2 caractères')
      .max(50, 'Le prénom ne peut pas dépasser 50 caractères'),
    last_name: yup
      .string()
      .required('Le nom est requis')
      .min(2, 'Le nom doit contenir au moins 2 caractères')
      .max(50, 'Le nom ne peut pas dépasser 50 caractères'),
    email: yup
      .string()
      .required('L\'email est requis')
      .email('Format email invalide')
      .max(255, 'L\'email ne peut pas dépasser 255 caractères'),
    password: yup
      .string()
      .required('Le mot de passe est requis')
      .min(8, 'Le mot de passe doit contenir au moins 8 caractères')
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, 
        'Le mot de passe doit contenir au moins une majuscule, une minuscule, un chiffre et un caractère spécial'),
    password_confirmation: yup
      .string()
      .required('La confirmation du mot de passe est requise')
      .oneOf([yup.ref('password')], 'Les mots de passe ne correspondent pas')
  })
);

const { errors } = useForm({ validationSchema: schema });

const handleSubmit = async (values) => {
  isSubmitting.value = true;
  
  try {
    await authService.register({
      first_name: values.first_name,
      last_name: values.last_name,
      email: values.email,
      password: values.password
    });
    
    router.push('/login?message=registration_success');
  } catch (error) {
    console.error('Registration failed:', error);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
