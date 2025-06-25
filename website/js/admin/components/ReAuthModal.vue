<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-60 z-50 flex justify-center items-center">
    <div class="bg-white p-8 rounded-lg shadow-2xl w-full max-w-sm">
      <h2 class="text-xl font-bold mb-2">Session Expired</h2>
      <p class="text-gray-600 mb-4">For your security, please re-enter your password to continue.</p>
      <form @submit.prevent="submit">
        <div class="mb-4">
          <label for="reauth-password" class="block text-sm font-medium text-gray-700">Password</label>
          <input 
            id="reauth-password" 
            type="password" 
            v-model="password" 
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
            ref="passwordInput"
          >
        </div>
        <div v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</div>
        <div class="flex justify-between items-center">
            <button 
                type="button" 
                @click="handleLogout" 
                class="text-sm text-gray-600 hover:text-indigo-600"
            >
                Log Out Instead
            </button>
            <button 
                type="submit" 
                :disabled="isLoading"
                class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300"
            >
                Continue
            </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
    isOpen: Boolean,
});
const emit = defineEmits(['submit', 'logout']);

const password = ref('');
const error = ref(null);
const isLoading = ref(false);
const passwordInput = ref(null);

watch(() => props.isOpen, (newVal) => {
    if (newVal) {
        // Reset state when modal opens and focus input
        password.value = '';
        error.value = null;
        isLoading.value = false;
        nextTick(() => {
            passwordInput.value?.focus();
        });
    }
});

const submit = async () => {
    if (!password.value) return;
    isLoading.value = true;
    error.value = null;
    try {
        await emit('submit', password.value);
    } catch (e) {
        error.value = "Invalid password. Please try again.";
    } finally {
        isLoading.value = false;
    }
};

const handleLogout = () => {
    emit('logout');
};
</script>
