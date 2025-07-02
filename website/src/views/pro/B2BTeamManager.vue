<template>
  <div class="bg-white p-6 rounded-lg shadow">
    <h3 class="text-lg font-medium leading-6 text-gray-900">Team Management</h3>
    <p class="mt-1 text-sm text-gray-500">Invite and manage users for your company account.</p>

    <!-- Invite User Form -->
    <VeeForm class="mt-6 border-b pb-6" @submit="handleInvite" :validation-schema="inviteSchema" v-slot="{ isSubmitting }">
      <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-6 sm:gap-x-4">
        <div class="sm:col-span-2">
          <label class="block text-sm font-medium text-gray-700">First Name</label>
          <VeeField type="text" name="first_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
          <VeeErrorMessage name="first_name" class="text-sm text-red-600 mt-1" />
        </div>
        <div class="sm:col-span-2">
          <label class="block text-sm font-medium text-gray-700">Last Name</label>
          <VeeField type="text" name="last_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
          <VeeErrorMessage name="last_name" class="text-sm text-red-600 mt-1" />
        </div>
        <div class="sm:col-span-2">
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <VeeField type="email" name="email" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
          <VeeErrorMessage name="email" class="text-sm text-red-600 mt-1" />
        </div>
      </div>
      <div class="mt-4 text-right">
        <button type="submit" :disabled="isSubmitting" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark disabled:bg-gray-400">
          Invite User
        </button>
      </div>
    </VeeForm>

    <!-- Users List -->
    <div class="mt-6">
      <h4 class="text-md font-medium text-gray-800">Current Users</h4>
      <div v-if="store.isLoading" class="mt-4 text-center">Loading users...</div>
      <ul v-else-if="store.users.length" role="list" class="divide-y divide-gray-200 mt-4">
        <li v-for="user in store.users" :key="user.id" class="py-4 flex justify-between items-center">
          <div>
            <p class="text-sm font-medium text-gray-900">{{ user.first_name }} {{ user.last_name }}</p>
            <p class="text-sm text-gray-500">{{ user.email }}</p>
          </div>
          <button @click="handleRemoveUser(user.id)" class="text-sm font-medium text-red-600 hover:text-red-800" :disabled="isCurrentUser(user.id)">
            Remove
          </button>
        </li>
      </ul>
      <p v-else class="mt-4 text-sm text-gray-500">No other users found for this account.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useB2BStore } from '@/stores/b2b';
import { useUserStore } from '@/stores/user';
import { object as yupObject, string as yupString } from 'yup';
import { Form as VeeForm, Field as VeeField, ErrorMessage as VeeErrorMessage } from 'vee-validate';

const store = useB2BStore();
const userStore = useUserStore();

const isCurrentUser = (id) => userStore.user?.id === id;

const inviteSchema = yupObject({
  first_name: yupString().required('First name is required'),
  last_name: yupString().required('Last name is required'),
  email: yupString().email('Must be a valid email').required('Email is required'),
});

onMounted(() => {
  store.fetchB2BUsers();
});

const handleInvite = async (values, { resetForm }) => {
  const success = await store.inviteB2BUser(values);
  if (success) {
    resetForm();
    await store.fetchB2BUsers(); // Refresh the list
  }
};

const handleRemoveUser = async (userId) => {
  if (confirm('Are you sure you want to remove this user from the account?')) {
    await store.removeB2BUser({ user_id: userId });
  }
};
</script>
