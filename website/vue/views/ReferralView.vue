<template>
  <div class="container mx-auto p-8">
    <h1 class="text-3xl font-bold text-center mb-6">Maison Truvra Referral Program</h1>
    
    <div class="text-center mb-8">
        <p class="text-lg">Share the love for truffles and earn exclusive rewards.</p>
    </div>

    <div v-if="userStore.isLoggedIn && referralCode" class="text-center p-6 bg-gray-100 rounded-lg">
        <p class="text-xl">Your personal referral code:</p>
        <p class="text-3xl font-bold text-primary my-2">{{ referralCode }}</p>
        <div class="flex justify-center space-x-4 mt-4">
             <button @click="shareByEmail" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Email</button>
            <button @click="shareByWhatsapp" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">WhatsApp</button>
            <button @click="shareByInstagram" class="px-4 py-2 bg-pink-500 text-white rounded hover:bg-pink-600">Instagram</button>
        </div>
    </div>
     <div v-else class="text-center">
        <p>Please log in to get your referral code.</p>
    </div>

    <div class="mt-12">
      <h2 class="text-2xl font-semibold text-center mb-4">How It Works</h2>
      <div class="max-w-2xl mx-auto">
        <ol class="list-decimal list-inside space-y-2">
            <li>Share your unique referral code with friends and colleagues.</li>
            <li>They get a discount on their first order.</li>
            <li>You earn rewards for every successful referral.</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from '../../js/stores/user';
import { apiClient } from '../../js/api-client';

const userStore = useUserStore();
const referralCode = ref('');

onMounted(async () => {
    if(userStore.isLoggedIn) {
        const response = await apiClient.get('/b2b/loyalty/referral-code');
        if (response.data.referral_code) {
            referralCode.value = response.data.referral_code;
        }
    }
});

const referralLink = computed(() => {
  if (referralCode.value) {
    return `${window.location.origin}/register?ref=${referralCode.value}`;
  }
  return '';
});

const shareByEmail = () => {
  const subject = "Invitation to Maison Truvra";
  const body = `Join me on Maison Truvra and get the best truffles! Use my referral link: ${referralLink.value}`;
  window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
};

const shareByWhatsapp = () => {
  const text = `Join me on Maison Truvra and get the best truffles! Use my referral link: ${referralLink.value}`;
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
};

const shareByInstagram = () => {
  // Instagram does not support direct sharing with pre-filled text. 
  // We can copy the link to the clipboard and instruct the user.
  navigator.clipboard.writeText(referralLink.value).then(() => {
    alert('Referral link copied to clipboard! Paste it in your Instagram story or bio.');
  });
};

</script>
