// website/source/js/stores/user.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '../api-client.js';

export const useUserStore = defineStore('user', () => {
    // STATE
    const profile = ref(null);
    const orders = ref([]);
    const isAuthenticated = ref(false);
    const isLoading = ref(false);

    // ACTIONS
    async function fetchProfile() {
        isLoading.value = true;
        try {
            const data = await apiClient.get('/account/profile');
            profile.value = data;
            isAuthenticated.value = true;
        } catch (error) {
            profile.value = null;
            isAuthenticated.value = false;
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchOrders() {
        isLoading.value = true;
        try {
            const data = await apiClient.get('/account/orders');
            orders.value = data.orders;
        } catch(error) {
            console.error("Failed to fetch orders:", error);
        } finally {
            isLoading.value = false;
        }
    }
    
    // Add login/logout/register actions similar to the B2B authStore if needed

    return { profile, orders, isAuthenticated, isLoading, fetchProfile, fetchOrders };
});
