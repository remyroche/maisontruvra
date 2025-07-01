import { defineStore } from 'pinia';
import api from '@/services/api';

export const useB2BStore = defineStore('b2b', {
  state: () => ({
    quotes: [],
    currentQuote: null,
  }),
  actions: {
    async submitQuoteRequest(quoteData) {
      try {
        const response = await api.post('/b2b/quotes/request', quoteData);
        return response.data;
      } catch (error) {
        console.error('Quote request submission failed:', error.response?.data);
        throw error;
      }
    },
    async fetchQuotes() {
      try {
        const response = await api.get('/admin/quotes'); // Assuming an admin endpoint exists
        this.quotes = response.data;
      } catch (error) {
        console.error('Failed to fetch quotes:', error.response?.data);
      }
    },
    async fetchQuoteDetails(quoteId) {
      try {
        const response = await api.get(`/admin/quotes/${quoteId}`); // Assuming an admin endpoint exists
        this.currentQuote = response.data;
      } catch (error) {
        console.error(`Failed to fetch quote ${quoteId}:`, error.response?.data);
      }
    },
    async respondAndAddToCart(quoteId, responseData) {
      try {
        // This should call the new backend endpoint
        const response = await api.post(`/quotes/${quoteId}/respond-and-add`, responseData);
        return response.data;
      } catch (error) {
        console.error(`Failed to respond to quote ${quoteId}:`, error.response?.data);
        throw error;
      }
    },
  },
});
