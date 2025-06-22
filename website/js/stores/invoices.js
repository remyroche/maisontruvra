// website/source/js/stores/invoices.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '../api-client.js';

export const useInvoiceStore = defineStore('invoices', () => {
    // STATE
    const invoices = ref([]);
    const isLoading = ref(false);

    // ACTIONS
    async function fetchInvoices() {
        isLoading.value = true;
        try {
            const data = await apiClient.get('/b2b/invoices');
            invoices.value = data.invoices;
        } catch (error) {
            console.error("Impossible de charger l'historique des factures.", error);
        } finally {
            isLoading.value = false;
        }
    }

    return { invoices, isLoading, fetchInvoices };
});
