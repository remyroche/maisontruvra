<template>
  <div>
    <h2 class="text-2xl font-bold leading-9 tracking-tight text-gray-900">Créer un compte</h2>
  </div>
  <div class="mt-10">
    <form class="space-y-6" @submit.prevent="handleRegister">
      <!-- Using the new generic UserDetailsForm -->
      <UserDetailsForm v-model="form" :include-password="true" />

      <div>
        <button type="submit"
          class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
          S'inscrire
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';
import UserDetailsForm from '@/components/forms/UserDetailsForm.vue';
import { useNotificationStore } from '@/stores/notification';

const userStore = useUserStore();
const router = useRouter();
const notificationStore = useNotificationStore();

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
});

const handleRegister = async () => {
  try {
    await userStore.register(form.value);
    router.push({ name: 'AccountDashboard' });
  } catch (error) {
    notificationStore.addNotification(error.message || 'Registration failed.', 'error');
  }
};
</script>
