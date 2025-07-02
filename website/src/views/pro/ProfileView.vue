<template>
  <div class="space-y-8">
    <h1 class="text-3xl font-bold">My Professional Profile</h1>

    <div v-if="b2bStore.profile" class="bg-white p-6 rounded-lg shadow space-y-4">
      <h2 class="text-xl font-semibold">Company Details</h2>
      <p><strong>Company Name:</strong> {{ b2bStore.profile.company_name }}</p>
      <p><strong>VAT Number:</strong> {{ b2bStore.profile.vat_number }}</p>
      <!-- Add more B2B profile details here -->
    </div>

    <!-- User Details (shared component) -->
    <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-xl font-semibold mb-4">Personal Details</h2>
        <UserDetailsForm />
    </div>

    <!-- Password Change (shared component) -->
    <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-xl font-semibold mb-4">Change Password</h2>
        <PasswordChangeForm />
    </div>

    <!-- Delete Account Section -->
    <div class="bg-white p-6 rounded-lg shadow border border-red-200">
      <h3 class="text-lg font-bold text-red-700">Delete Professional Account</h3>
      <p class="text-gray-600 mt-2 mb-4">
        This action will permanently delete your professional account, your user profile, and all associated data. This cannot be undone.
      </p>
      <button @click="showConfirmModal = true" class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">
        Request Account Deletion
      </button>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-center items-center p-4">
      <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h3 class="text-lg font-bold">Confirm Account Deletion</h3>
        <p class="my-4">Are you sure you want to delete your professional account? This action is irreversible.</p>
        <div class="flex justify-end space-x-4">
          <button @click="showConfirmModal = false" class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300">Cancel</button>
          <button @click="confirmB2BDeletion" class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">I'm Sure, Delete My Account</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useB2BStore } from '@/stores/b2b';
import UserDetailsForm from '@/components/forms/UserDetailsForm.vue';
import PasswordChangeForm from '@/components/auth/PasswordChangeForm.vue';

const b2bStore = useB2BStore();
const router = useRouter();
const showConfirmModal = ref(false);

onMounted(() => {
  // Assuming you have a method to fetch the B2B profile
  // b2bStore.fetchProfile(); 
});

async function confirmB2BDeletion() {
  showConfirmModal.value = false;
  const success = await b2bStore.deleteB2BAccount();
  if (success) {
    router.push('/');
  }
}
</script>
