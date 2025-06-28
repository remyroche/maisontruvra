import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '@/services/api';

export const useUserStore = defineStore('user', () => {
  const profile = ref(null);
  const isLoggedIn = ref(null); // null: unknown, false: logged out, true: logged in

  async function checkAuthStatus() {
    try {
      const data = await apiClient.get('/auth/status'); // Assuming a public auth status endpoint
      profile.value = data.user;
      isLoggedIn.value = data.is_authenticated;
    } catch (error) {
      profile.value = null;
      isLoggedIn.value = false;
    }
  }

  async function fetchUserProfile() {
    await checkAuthStatus(); // Re-use the auth status check to refresh profile
  }

  return { profile, isLoggedIn, checkAuthStatus, fetchUserProfile };
});