/*
 * FILENAME: website/js/stores/adminInvoices.js
 * DESCRIPTION: New Pinia store for fetching invoice data.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminInvoiceStore = defineStore('adminInvoices', () => {
    const invoices = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchInvoices() {
        isLoading.value = true;
        error.value = null;
        try {
            // Assuming an endpoint exists to fetch all invoices
            const response = await adminApiClient.get('/invoices');
            invoices.value = response.data.invoices;
        } catch (err) {
            error.value = 'Failed to fetch invoices.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

    return { invoices, isLoading, error, fetchInvoices };
});
