import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminInvoicesStore = defineStore('adminInvoices', {
  state: () => ({
    invoices: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchInvoices() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/invoices');
        this.invoices = response.data;
      } catch (e) {
        this.error = 'Failed to fetch invoices.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
    async downloadInvoice(invoiceId) {
        try {
            const response = await apiClient.get(`/invoices/${invoiceId}/download`, {
                responseType: 'blob', // Important for file downloads
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `invoice_${invoiceId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (e) {
            this.error = "Failed to download invoice."
            console.error(this.error, e);
        }
    }
  },
});
