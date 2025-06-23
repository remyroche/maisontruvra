<template>
  <div>
    <div v-if="loading" class="text-center p-8">
      <p>Chargement du programme de fidélité...</p>
    </div>
    <div v-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert">
        <p class="font-bold">Erreur</p>
        <p>{{ error }}</p>
    </div>

    <div v-if="!loading && !error">
      <!-- Page Header -->
      <h2 class="text-2xl font-bold mb-4 text-brand-dark-gray">Programme de Fidélité & Parrainage</h2>
      <p class="mb-8 text-gray-600">Gagnez des points, débloquez des remises exclusives et soyez récompensé pour votre fidélité.</p>

      <!-- User's Current Status & Referrals -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        
        <!-- MODIFIED: Using the LoyaltyStatus component -->
        <LoyaltyStatus :status="userStatus" />

        <!-- Referral Section -->
        <div>
            <h3 class="text-xl font-semibold mb-4 text-brand-burgundy">Parrainez un Professionnel</h3>
            <div class="bg-gray-100 p-6 rounded-lg">
                <p class="text-gray-700 mb-2">Partagez votre code pour gagner <strong>0.1 point</strong> pour chaque <strong>1€</strong> dépensé par vos filleuls !</p>
                <div class="relative">
                    <input type="text" readonly :value="userStatus?.referralCode || 'N/A'" class="w-full bg-white border border-gray-300 rounded-md p-2 pr-20 text-gray-600">
                    <button @click="copyReferralCode" class="absolute inset-y-0 right-0 px-4 bg-gray-200 text-gray-700 font-semibold rounded-r-md hover:bg-gray-300 transition">Copier</button>
                </div>
            </div>
        </div>
      </div>

      <!-- Tier Information Section (Logic from B2BLoyalty.vue) -->
      <TierBenefits :tiers="loyaltyTiers" :userTier="userStatus?.tier" />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { apiClient } from '@/js/api-client.js'; // Adjust path

// Import the reusable child components
import LoyaltyStatus from './LoyaltyStatus.vue';
import TierBenefits from './B2BLoyalty.vue'; // Assuming B2BLoyalty.vue is refactored to be TierBenefits

const loading = ref(true);
const error = ref(null);
const userStatus = ref(null);
const loyaltyTiers = ref([]);
const ambassadorTier = ref(null);

async function fetchLoyaltyData() {
    loading.value = true;
    error.value = null;
    try {
        const response = await apiClient.get('/b2b/loyalty/program-details');
        userStatus.value = response.data.userStatus;
        loyaltyTiers.value = response.data.tierDiscounts;
    } catch (err) {
        error.value = err.message || 'Impossible de charger les détails du programme de fidélité.';
        console.error(err);
    } finally {
        loading.value = false;
    }
}

function copyReferralCode() {
    const code = userStatus.value?.referralCode;
    if (!code) return;
    navigator.clipboard.writeText(code).then(() => {
        showNotification('Code de parrainage copié !');
    });
}

function showNotification(message) {
    const area = document.getElementById('notification-area');
    if (!area) return;
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.className = 'notification notification-success';
    area.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => area.removeChild(notification), 300);
    }, 3000);
}

onMounted(() => {
    fetchLoyaltyData();
});
</script>

<style scoped>
/* Scoped styles can be added here if needed */
</style>
