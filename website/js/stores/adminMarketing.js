/*
 * FILENAME: website/js/stores/adminMarketing.js
 * DESCRIPTION: New Pinia store for managing marketing tools like Newsletters and Quotes.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminMarketingStore = defineStore('adminMarketing', () => {
    const subscribers = ref([]);
    const quotes = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchSubscribers() {
        // ... API call to fetch newsletter subscribers
    }
    
    async function fetchQuotes() {
        // ... API call to fetch quote requests
    }

    return { subscribers, quotes, isLoading, error, fetchSubscribers, fetchQuotes };
});
