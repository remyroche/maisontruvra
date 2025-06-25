<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Setup Multi-Factor Authentication</h1>
    <div v-if="!mfaDetails.qrCode">
        <p>Click the button to generate an MFA QR code. Scan it with your authenticator app.</p>
        <button @click="generateMfa" class="bg-blue-500 text-white px-4 py-2 rounded">Generate QR Code</button>
    </div>
    <div v-else>
        <img :src="mfaDetails.qrCode" alt="MFA QR Code">
        <form @submit.prevent="verifyMfa">
            <input v-model="mfaToken" placeholder="Enter MFA Token" class="border rounded p-2 mt-4 mr-2">
            <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded">Verify</button>
        </form>
    </div>
     <div v-if="mfaError" class="text-red-500 mt-4">{{ mfaError }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '@/js/common/adminApiClient';

const mfaDetails = ref({});
const mfaToken = ref('');
const mfaError = ref(null);


const generateMfa = async () => {
    try {
        const response = await apiClient.post('/auth/mfa/setup');
        mfaDetails.value = response.data;
    } catch (error) {
        mfaError.value = 'Failed to generate MFA details.';
    }
};

const verifyMfa = async () => {
    try {
        await apiClient.post('/auth/mfa/verify', { token: mfaToken.value });
        alert('MFA setup successful!');
        mfaDetails.value = {};
    } catch (error) {
         mfaError.value = 'Invalid MFA token.';
    }
};

</script>
