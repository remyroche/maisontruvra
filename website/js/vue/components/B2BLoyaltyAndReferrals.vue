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

      <!-- User's Current Status & Referrals Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        
        <!-- Loyalty Status Component -->
        <LoyaltyStatus :status="userStatus" />

        <!-- Points Breakdown Card -->
        <div class="p-6 bg-white rounded-lg shadow-md">
            <h3 class="text-xl font-semibold text-dark-brown mb-4">Origine de vos Points</h3>
            <div v-if="!pointsBreakdown" class="text-center py-4">
                <p>Calcul des points...</p>
            </div>
            <div v-else class="space-y-4 text-gray-700">
                <div class="flex justify-between items-center pb-2 border-b">
                    <span>Points de vos achats</span>
                    <span class="font-bold text-lg text-truffle-burgundy">{{ pointsBreakdown.from_purchases }}</span>
                </div>
                <div class="flex justify-between items-center pb-2 border-b">
                    <span>Points de vos parrainages</span>
                    <span class="font-bold text-lg text-green-600">{{ pointsBreakdown.from_referrals }}</span>
                </div>
                <div class="flex justify-between items-center pt-2 font-bold">
                    <span>Total des Points Actifs</span>
                    <span class="text-xl text-dark-brown">{{ pointsBreakdown.total }}</span>
                </div>
            </div>
        </div>

      </div>

      <!-- Referral Section -->
      <div class="mb-12">
          <h3 class="text-xl font-semibold mb-4 text-brand-burgundy">Parrainez un Professionnel</h3>
          <div class="bg-gray-100 p-6 rounded-lg">
              <p class="text-gray-700 mb-2">Partagez votre code pour gagner <strong>0.1 point</strong> pour chaque <strong>1€</strong> dépensé par vos filleuls !</p>
              <div class="relative">
                  <input type="text" readonly :value="userStatus?.referralCode || 'N/A'" class="w-full bg-white border border-gray-300 rounded-md p-2 pr-20 text-gray-600">
                  <button @click="copyReferralCode" class="absolute inset-y-0 right-0 px-4 bg-gray-200 text-gray-700 font-semibold rounded-r-md hover:bg-gray-300 transition">Copier</button>
              </div>
          </div>
      </div>

      <!-- Tier Information Section -->
      <TierBenefits :tiers="loyaltyTiers" :userTier="userStatus?.tier" />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { apiClient } from '@/js/api-client.js'; 
import { useNotificationStore } from '@/js/stores/notification';

// Import the reusable child components
import LoyaltyStatus from './LoyaltyStatus.vue';
import TierBenefits from './B2BLoyalty.vue';

const loading = ref(true);
const error = ref(null);
const userStatus = ref(null);
const loyaltyTiers = ref([]);
const pointsBreakdown = ref(null);
const notificationStore = useNotificationStore();


async function fetchLoyaltyData() {
    loading.value = true;
    error.value = null;
    try {
        // Fetch all data in parallel
        const [detailsRes, breakdownRes] = await Promise.all([
            apiClient.get('/b2b/loyalty/program-details'),
            apiClient.get('/api/b2b/loyalty/points-breakdown')
        ]);

        userStatus.value = detailsRes.data.userStatus;
        loyaltyTiers.value = detailsRes.data.tierDiscounts;
        pointsBreakdown.value = breakdownRes.data;

    } catch (err) {
        const errorMessage = err.response?.data?.error || err.message || 'Impossible de charger les données de fidélité.';
        error.value = errorMessage;
        notificationStore.showNotification(errorMessage, 'error');
        console.error(err);
    } finally {
        loading.value = false;
    }
}

function copyReferralCode() {
    const code = userStatus.value?.referralCode;
    if (!code) return;
    navigator.clipboard.writeText(code).then(() => {
        notificationStore.showNotification('Code de parrainage copié !', 'success');
    });
}

onMounted(() => {
    fetchLoyaltyData();
});
</script>

<style scoped>
/* Scoped styles can be added here if needed */
</style>
