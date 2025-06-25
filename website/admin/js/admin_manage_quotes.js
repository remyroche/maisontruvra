import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminQuotesStore = defineStore('adminQuotes', {
  state: () => ({
    quotes: [],
    quote: null,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchQuotes() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/quotes');
        this.quotes = response.data;
      } catch (e) {
        this.error = 'Failed to fetch quotes.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
    async fetchQuoteDetails(quoteId) {
        this.isLoading = true;
        this.error = null;
        try {
            const response = await apiClient.get(`/quotes/${quoteId}`);
            this.quote = response.data;
        } catch(e) {
            this.error = `Failed to fetch quote #${quoteId}`;
        } finally {
            this.isLoading = false;
        }
    },
    async convertQuoteToOrder(quoteId) {
        try {
            await apiClient.post(`/quotes/${quoteId}/convert`);
            await this.fetchQuotes(); // Refresh list
        } catch(e) {
            this.error = 'Failed to convert quote to order.';
            throw e;
        }
    },
    async deleteQuote(quoteId) {
      try {
        await apiClient.delete(`/quotes/${quoteId}`);
        await this.fetchQuotes();
      } catch (e) {
        this.error = 'Failed to delete quote.';
      }
    },
  },
});
