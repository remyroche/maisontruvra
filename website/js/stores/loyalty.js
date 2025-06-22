// website/source/js/stores/loyalty.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '../api-client.js';

export const useLoyaltyStore = defineStore('loyalty', () => {
    // STATE
    const status = ref({
        tier_name: '',
        points: 0,
        progress_percentage: 0,
        next_tier_message: '',
        tiers: []
    });
    const referral = ref({
        code: '',
        points_per_euro: 0.1,
        yearly_earnings: 0
    });
    const isLoading = ref(false);

    // ACTIONS
    async function fetchLoyaltyData() {
        isLoading.value = true;
        try {
            const [loyaltyStatus, referralInfo, referralStats] = await Promise.all([
                apiClient.get('/b2b/loyalty/status'),
                apiClient.get('/b2b/referral/info'),
                apiClient.get('/b2b/referral/stats?period=365d')
            ]);
            status.value = loyaltyStatus;
            referral.value.code = referralInfo.code;
            referral.value.points_per_euro = referralInfo.points_per_euro;
            referral.value.yearly_earnings = referralStats.total_points_earned;
        } catch (error) {
            console.error("Impossible de charger les données de fidélité et de parrainage.", error);
            // Ne pas bloquer l'interface pour une erreur non critique
        } finally {
            isLoading.value = false;
        }
    }

    return { status, referral, isLoading, fetchLoyaltyData };
});
