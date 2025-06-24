/*
 * FILENAME: website/js/stores/adminMarketing.js
 * DESCRIPTION: Pinia store for managing marketing tools.
 * UPDATED: Implemented functionality for Newsletters and Quotes.
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
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/newsletter/subscribers');
            subscribers.value = response.data.subscribers;
        } catch(err) {
            error.value = 'Failed to fetch subscribers.';
        } finally {
            isLoading.value = false;
        }
    }
    
    async function fetchQuotes() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/quotes');
            quotes.value = response.data.quotes;
        } catch(err) {
            error.value = 'Failed to fetch quotes.';
        } finally {
            isLoading.value = false;
        }
    }

    return { subscribers, quotes, isLoading, error, fetchSubscribers, fetchQuotes };
});
